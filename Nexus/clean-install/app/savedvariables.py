"""Streaming parser for WoW's line-oriented SavedVariables output. Never evaluates Lua.

Keeps strings as bytes when requested, including Auctionator CBOR. It deliberately
rejects executable Lua and nonstandard formatting rather than guessing.
"""
import math
import re

FIELD = re.compile(rb'\[("(?:\\.|[^"\\])*"|-?\d+)\]\s*=\s*(.*)')
ASSIGN = re.compile(rb'([A-Za-z_][A-Za-z_0-9]*)\s*=\s*(.*)')
STRING = re.compile(rb'"(?:\\.|[^"\\])*"')
NUMBER = re.compile(rb'-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?')


def scalar(raw, binary=False):
    if STRING.fullmatch(raw):
        def escape(m):
            v = m[1]
            if v.isdigit():
                n = int(v)
                if n > 255:
                    raise ValueError('Invalid byte escape')
                return bytes([n])
            escapes = {b'n': b'\n', b'r': b'\r', b't': b'\t', b'a': b'\a',
                       b'b': b'\b', b'f': b'\f', b'v': b'\v', b'"': b'"', b'\\': b'\\'}
            if v not in escapes:
                raise ValueError('Unsupported string escape')
            return escapes[v]
        value = re.sub(rb'\\(\d{1,3}|.)', escape, raw[1:-1])
        return value if binary else value.decode('utf-8', errors='strict')
    if raw in (b'true', b'false', b'nil'):
        return {b'true': True, b'false': False, b'nil': None}[raw]
    if NUMBER.fullmatch(raw):
        value = float(raw) if any(c in raw for c in (b'.', b'e', b'E')) else int(raw)
        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError('Nonfinite number')
        return value
    raise ValueError('Unsupported SavedVariables value; executable Lua rejected')


def read_lua(path, binary=False):
    root = {}
    stack = [root]
    indexes = [0]
    with open(path, 'rb') as stream:
        for number, line in enumerate(stream, 1):
            value = line.strip().removesuffix(b',')
            if not value or value.startswith(b'--'):
                continue
            try:
                if value == b'}':
                    if len(stack) == 1:
                        raise ValueError('Unexpected table end')
                    stack.pop(); indexes.pop()
                    continue
                field = FIELD.fullmatch(value)
                assignment = ASSIGN.fullmatch(value)
                if field:
                    key, value = scalar(field[1], binary), field[2]
                elif assignment:
                    key, value = assignment[1], assignment[2]
                    key = key if binary else key.decode('ascii')
                else:
                    if len(stack) == 1:
                        raise ValueError('Expected global assignment')
                    indexes[-1] += 1
                    key = indexes[-1]
                if key in stack[-1]:
                    raise ValueError('Duplicate key')
                if value == b'{':
                    if len(stack) >= 100:
                        raise ValueError('Nesting limit exceeded')
                    child = {}; stack[-1][key] = child
                    stack.append(child); indexes.append(0)
                else:
                    stack[-1][key] = scalar(value, binary)
            except (ValueError, UnicodeError) as exc:
                raise ValueError(f'{path.name}:{number}: {exc}') from exc
    if len(stack) != 1:
        raise ValueError('Incomplete SavedVariables file')
    return root
