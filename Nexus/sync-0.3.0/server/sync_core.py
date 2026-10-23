"""Bounded, data-only sync protocol. No shell evaluation or Lua execution."""
import hashlib
import json
import os
import re
import stat
import tempfile
from pathlib import Path

LIMIT = 64 * 1024 * 1024
HASH = re.compile(r'^[0-9a-f]{64}$')

def parse_command(command):
    parts = command.split()
    if len(parts) == 2 and parts[0] == 'status' and HASH.fullmatch(parts[1]):
        return parts[0], parts[1], 0
    if (len(parts) == 3 and parts[0] == 'put' and HASH.fullmatch(parts[1])
            and parts[2].isdigit() and 0 < int(parts[2]) <= LIMIT):
        return parts[0], parts[1], int(parts[2])
    raise ValueError('Invalid sync command')

def atomic_json(path, value):
    fd, name = tempfile.mkstemp(prefix='.tmp-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as stream:
            json.dump(value, stream)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(name, 0o644)  # Receipts contain counters/hashes only, never source data.
        os.replace(name, path)
        sync_dir(path.parent)
    finally:
        if os.path.exists(name):
            os.unlink(name)

def sync_dir(path):
    if os.name == 'posix':
        fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)

def receive(stream, directory, digest, size, suffix='.lua'):
    fd, name = tempfile.mkstemp(prefix='.upload-', dir=directory)
    try:
        h = hashlib.sha256()
        with os.fdopen(fd, 'wb') as out:
            remaining = size
            while remaining:
                block = stream.read(min(1024 * 1024, remaining))
                if not block:
                    raise ValueError('Incomplete upload')
                out.write(block)
                h.update(block)
                remaining -= len(block)
            if stream.read(1):
                raise ValueError('Extra upload bytes')
            if h.hexdigest() != digest:
                raise ValueError('SHA256 mismatch')
            out.flush()
            os.fsync(out.fileno())
        os.chmod(name, 0o600)
        os.replace(name, directory / (digest + suffix))
        sync_dir(directory)
    finally:
        if os.path.exists(name):
            os.unlink(name)

def verified_read(path, digest):
    fd = os.open(path, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_NONBLOCK', 0))
    with os.fdopen(fd, 'rb') as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or not 0 < info.st_size <= LIMIT:
            raise ValueError('Invalid spool file')
        raw = stream.read(LIMIT + 1)
    if len(raw) > LIMIT or hashlib.sha256(raw).hexdigest() != digest:
        raise ValueError('Spool checksum mismatch')
    return raw

def import_result(text):
    result = json.loads(text)
    if result.get('status') not in ('imported', 'already_imported'):
        raise ValueError('Importer did not confirm commit')
    for key in ('inserted', 'records', 'import_id'):
        if type(result.get(key)) is not int or result[key] < 0:
            raise ValueError('Invalid importer receipt')
    return {key: result[key] for key in ('status', 'inserted', 'records', 'import_id')}
