"""Read existing snapshot manifests without changing any historical files."""
import argparse
import json
from pathlib import Path
from bundle import create_bundle


def queue_history(source, destination):
    destination.mkdir(parents=True, exist_ok=True)
    count = 0
    for manifest in source.rglob('*.json'):
        data = json.loads(manifest.read_text(encoding='utf-8-sig'))
        if not isinstance(data, dict) or not {'sha256', 'source', 'namespace', 'raw_bytes'} <= data.keys():
            continue
        temporary = destination / 'history.tmp'
        digest = create_bundle(manifest, temporary)
        temporary.replace(destination / (digest + '.bundle'))
        count += 1
    if not count:
        raise ValueError('No historical snapshot manifests found')
    print(f'Queued {count} historical snapshots')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=Path)
    parser.add_argument('destination', type=Path)
    args = parser.parse_args()
    queue_history(args.source, args.destination)
