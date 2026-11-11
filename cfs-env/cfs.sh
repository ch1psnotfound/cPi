#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONTAINER="${CFS_CONTAINER:-cpi-cfs-dev}"
ACTION="${1:-help}"
case "$ACTION" in
  build|test|smoke|verify|run|shell)
    docker start "$CONTAINER" >/dev/null
    ;;
esac
case "$ACTION" in
  build)
    mkdir -p "$ROOT/cfs/build-native_std"
    {
      docker exec "$CONTAINER" make native_std.prep &&
      docker exec "$CONTAINER" make -j4 native_std.install
    } 2>&1 | tee "$ROOT/cfs/build-native_std/cpi-build.log"
    ;;
  test)
    mkdir -p "$ROOT/cfs/build-native_std"
    docker exec -u 1000:1000 "$CONTAINER" ctest --test-dir build-native_std/native/default_cpu1 -j4 --timeout 30 --output-on-failure --output-junit /workspace/cfs/build-native_std/cpi-tests.xml 2>&1 | tee "$ROOT/cfs/build-native_std/cpi-test.log"
    ;;
  smoke)
    docker exec -u 1000:1000 -i "$CONTAINER" python3 - < "$ROOT/cfs-env/smoke.py"
    ;;
  verify)
    bash "$0" build
    RESULT=0
    bash "$0" test || RESULT=1
    bash "$0" smoke || RESULT=1
    exit "$RESULT"
    ;;
  run)
    docker exec -u 1000:1000 -it -w /workspace/cfs/build-native_std/exe/cpu1 "$CONTAINER" ./core-cpu1
    ;;
  shell)
    docker exec -it "$CONTAINER" bash
    ;;
  stop)
    docker stop "$CONTAINER"
    ;;
  *)
    echo 'Usage: bash cfs-env/cfs.sh {build|test|smoke|verify|run|shell|stop}'
    ;;
esac
