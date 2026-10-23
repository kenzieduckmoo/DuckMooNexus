#!/usr/bin/python3
import fcntl
import json
import os
import signal
import sys
from pathlib import Path
from sync_core import parse_command, receive, HASH

def main():
    os.umask(0o077)
    signal.alarm(180)
    original = os.environ.get('SSH_ORIGINAL_COMMAND', '')
    parts = original.split()
    suffix = '.lua'
    if len(parts)==3 and parts[0]=='put2' and HASH.fullmatch(parts[1]) and parts[2].isdigit() and 0<int(parts[2])<=512*1024**2:
        action,digest,size='put',parts[1],int(parts[2]);suffix='.bundle'
        signal.alarm(900)
    else:
        action, digest, size = parse_command(original)
    base = Path('/var/lib/duckmoo-sync')
    receipt = base / 'receipts' / (digest + '.json')
    if action == 'status':
        queued=(base/'inbox'/(digest+'.lua')).exists() or (base/'inbox'/(digest+'.bundle')).exists()
        print(receipt.read_text() if receipt.exists() else json.dumps({'status': 'queued' if queued else 'pending', 'sha256': digest}))
        return
    # Serialize reception and bound disk use even when a key is misused.
    with (base / 'inbox' / '.receive.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        files = list((base / 'inbox').glob('*.lua'))+list((base / 'inbox').glob('*.bundle'))
        if len(files) >= 64 or sum(p.stat().st_size for p in files)+size > 2 * 1024**3:
            raise ValueError('Inbox full; inspect server failures')
        for stale in (base / 'inbox').glob('.upload-*'):
            stale.unlink()  # Exclusive receive lock makes leftovers safe to remove.
        receive(sys.stdin.buffer, base / 'inbox', digest, size, suffix)
    print(json.dumps({'status': 'queued', 'sha256': digest}))

if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(json.dumps({'status': 'error', 'reason': type(exc).__name__}), file=sys.stderr)
        sys.exit(1)
