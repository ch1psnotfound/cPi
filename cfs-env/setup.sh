#!/usr/bin/env bash
# Configure a development container without generating a Dockerfile.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONTAINER="${CFS_CONTAINER:-cpi-cfs-dev}"
IMAGE='ubuntu:24.04@sha256:fe81560990fae86dc4743202b2cb4d3df98d0bcf949173cecef15ce1127ef852'
if [[ ! -f "$ROOT/cfs/Makefile" ]]; then
  echo 'Missing cFS checkout. Follow README clone instructions first.' >&2
  exit 1
fi
if docker container inspect "$CONTAINER" >/dev/null 2>&1; then
  EXPECTED="$ROOT/cfs"
  ACTUAL="$(docker inspect --format '{{range .Mounts}}{{if eq .Destination "/workspace/cfs"}}{{.Source}}{{end}}{{end}}' "$CONTAINER")"
  if [[ "$ACTUAL" != "$EXPECTED" ]]; then
    echo "Container $CONTAINER mounts a different source directory: $ACTUAL" >&2
    exit 1
  fi
  docker start "$CONTAINER" >/dev/null
else
  docker run -d --name "$CONTAINER" --platform linux/arm64 \
    --mount "type=bind,source=$ROOT/cfs,target=/workspace/cfs" \
    --workdir /workspace/cfs "$IMAGE" sleep infinity
fi
ENV_ARGS=(-e DEBIAN_FRONTEND=noninteractive)
# Example: CFS_APT_PROXY=http://host.docker.internal:7897 bash cfs-env/setup.sh
if [[ -n "${CFS_APT_PROXY:-}" ]]; then
  ENV_ARGS+=(-e "http_proxy=$CFS_APT_PROXY" -e "https_proxy=$CFS_APT_PROXY")
fi
docker exec "${ENV_ARGS[@]}" "$CONTAINER" sh -ec \
  'apt-get update && apt-get install -y --no-install-recommends build-essential cmake git gdb python3 ca-certificates pkg-config jq'
