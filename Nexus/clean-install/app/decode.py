"""Data-only SavedVariables parser and bundled Journalator codec bridge."""
import re
from pathlib import Path
from lupa.lua51 import LuaRuntime, lua_type

TOKEN = re.compile(rb'\s+|--[^\r\n]*|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?|[A-Za-z_][A-Za-z_0-9]*|[{}\[\]=,;]', re.S)

def parse(raw):
    tokens = []
    pos = 0
    while pos < len(raw):
        m = TOKEN.match(raw, pos)
        if not m:
            raise ValueError(f'Unsupported SavedVariables syntax at byte {pos}')
        t = m.group(); pos = m.end()
        if not t.isspace() and not t.startswith(b'--'):
            tokens.append(t)
    i = 0
    def take(expected=None):
        nonlocal i
        if i >= len(tokens): raise ValueError('Truncated SavedVariables')
        t = tokens[i]; i += 1
        if expected is not None and t != expected: raise ValueError(f'Expected {expected!r}')
        return t
    def string(t):
        def esc(m):
            v = m.group()[1:]
            if v.isdigit():
                n = int(v)
                if n > 255: raise ValueError('Invalid byte escape')
                return bytes([n])
            return {b'n':b'\n',b'r':b'\r',b't':b'\t',b'a':b'\a',b'b':b'\b',b'f':b'\f',b'v':b'\v'}.get(v,v)
        return re.sub(rb'\\(?:\d{1,3}|.)', esc, t[1:-1], flags=re.S)
    def value(depth=0):
        if depth > 100: raise ValueError('Table nesting limit exceeded')
        t = take()
        if t == b'{':
            d = {}; index = 1
            while tokens[i] != b'}':
                if tokens[i] == b'[':
                    take(); k = value(depth+1); take(b']'); take(b'='); v = value(depth+1)
                elif i+1 < len(tokens) and tokens[i+1] == b'=':
                    k = take(); take(b'='); v = value(depth+1)
                else:
                    k = index; index += 1; v = value(depth+1)
                if k in d: raise ValueError('Duplicate table key')
                d[k] = v
                if tokens[i] in (b',', b';'): take()
                elif tokens[i] != b'}': raise ValueError('Expected table separator')
            take(b'}'); return d
        if t[:1] in (b'"', b"'"): return string(t)
        if t in (b'true', b'false', b'nil'): return {b'true':True,b'false':False,b'nil':None}[t]
        if re.fullmatch(rb'-?\d+', t): return int(t)
        if re.fullmatch(rb'-?\d+\.\d+(?:[eE][+-]?\d+)?',t): return float(t)
        raise ValueError('Executable expressions are not allowed')
    result = {}
    while i < len(tokens):
        k = take()
        if not re.fullmatch(rb'JOURNALATOR_[A-Z_]+',k): raise ValueError('Unexpected global')
        if k in result: raise ValueError('Duplicate global')
        take(b'='); result[k] = value()
    return result

def native(v):
    if lua_type(v) == 'table': return {native(k):native(x) for k,x in v.items()}
    if isinstance(v,bytes): return v.decode('utf-8', errors='strict')
    return v

def decode(raw):
    sv = parse(raw)
    if sv.get(b'JOURNALATOR_LOGS') is not None: raise ValueError('Legacy JOURNALATOR_LOGS unsupported')
    archive = sv[b'JOURNALATOR_ARCHIVE']
    if archive[b'internalVersion'] != 1: raise ValueError('Unsupported Archivist version')
    lua = LuaRuntime(encoding=None, unpack_returned_tuples=True, max_memory=256*1024*1024)
    vendor = Path(__file__).parent/'vendor'
    ld = lua.execute((vendor/'LibDeflate.lua').read_bytes())
    ls = lua.execute((vendor/'LibSerialize.lua').read_bytes())
    for kind, stores in archive[b'stores'].items():
        if stores and kind != b'SometimesLocked': raise ValueError('Unsupported archive store type')
        for store_id, store in sorted(stores.items()):
            if store[b'version'] != 1: raise ValueError('Unsupported store version')
            encoded = store[b'data']
            compressed = ld.DecodeForPrint(ld, encoded)
            if compressed is None: raise ValueError('Invalid print encoding')
            inflated = ld.DecompressDeflate(ld, compressed)
            if isinstance(inflated,tuple): inflated = inflated[0]
            if inflated is None: raise ValueError('Invalid Deflate data')
            result = ls.Deserialize(ls, inflated)
            if not isinstance(result,tuple) or len(result)!=2 or result[0] is not True:
                raise ValueError('Invalid LibSerialize payload')
            data = native(result[1])
            if data and data.get('Version') not in range(1,16): raise ValueError('Unsupported Journalator store version')
            yield store_id.decode(), encoded.decode('ascii'), data



