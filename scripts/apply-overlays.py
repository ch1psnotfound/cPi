#!/usr/bin/env python3
"""Apply cPi-owned files to upstream checkouts; refuse conflicting local edits."""
from pathlib import Path
import argparse
import shutil


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Check without copying files')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    overlay_root = root / 'overlays'
    copies = []
    conflicts = []
    for source in sorted(overlay_root.rglob('*')):
        if not source.is_file():
            continue
        relative = source.relative_to(overlay_root)
        checkout = root / relative.parts[0]
        if not (checkout / '.git').exists():
            raise SystemExit(f'Initialize submodules first: {checkout.name}')
        target = root / relative
        if target.exists():
            if target.is_file() and target.read_bytes() == source.read_bytes():
                continue
            conflicts.append(str(relative))
        else:
            copies.append((source, target))
    if conflicts:
        raise SystemExit('Local files differ; reconcile with overlays before applying:\n' + '\n'.join(conflicts))
    if args.check:
        if copies:
            raise SystemExit('Missing overlays:\n' + '\n'.join(str(t.relative_to(root)) for _, t in copies))
        print('All overlays match their working copies.')
        return
    for source, target in copies:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        print(f'Applied {target.relative_to(root)}')
    print('All overlays match their working copies.')


if __name__ == '__main__':
    main()
