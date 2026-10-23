"""Bind successful isolated verification to the exact deployable source and image."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent


def fingerprint(root=ROOT):
    paths = []
    for folder in ('duckmoo-nexus', 'sync-0.3.0', 'sync-reference'):
        paths.extend(p for p in (root / folder).rglob('*')
                     if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc')
    paths.extend(root / name for name in
                 ('upgrade-server.sh', 'rollback-server.sh', 'verify-stack.sh', 'preflight.sh', 'release_gate.py'))
    digest = hashlib.sha256()
    for path in sorted(paths):
        digest.update(path.relative_to(root).as_posix().encode() + b'\0')
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


if __name__ == '__main__':
    action, image = sys.argv[1:]
    receipt = ROOT / '.verified-release.json'
    expected = {'source_sha256': fingerprint(), 'image_id': image}
    if action == 'record':
        receipt.write_text(json.dumps(expected, indent=2) + '\n')
    elif action == 'check':
        if not receipt.exists() or json.loads(receipt.read_text()) != expected:
            raise SystemExit('Run verify-stack.sh successfully for this exact release and image first.')
    else:
        raise SystemExit('Expected record or check')
