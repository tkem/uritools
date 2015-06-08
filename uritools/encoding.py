from string import hexdigits

from .chars import UNRESERVED

try:
    _fromhex = bytes.fromhex
except AttributeError:
    _fromhex = lambda x: chr(int(x, 16))

if isinstance(chr(0), bytes):
    _fromint = chr
else:
    _fromint = lambda i: bytes([i])


# RFC 3986 2.1: For consistency, URI producers and normalizers should
# use uppercase hexadecimal digits for all percent-encodings.
def _pctenc(byte):
    return ('%%%02X' % byte).encode()

_unreserved = frozenset(memoryview(UNRESERVED.encode('ascii')).tolist())

_encoded = {
    b'': [_fromint(i) if i in _unreserved else _pctenc(i) for i in range(256)]
}

_decoded = {
    (a + b).encode(): _fromhex(a + b) for a in hexdigits for b in hexdigits
}


def uriencode(uristring, safe='', encoding='utf-8', errors='strict'):
    """Encode a URI string or string component."""
    if isinstance(uristring, bytes):
        values = memoryview(uristring).tolist()
    else:
        values = memoryview(uristring.encode(encoding, errors)).tolist()
    if not isinstance(safe, bytes):
        safe = safe.encode('ascii')
    try:
        encode = _encoded[safe].__getitem__
    except KeyError:
        enclist = _encoded[b''][:]
        for i in memoryview(safe).tolist():
            enclist[i] = _fromint(i)
        _encoded[safe] = enclist
        encode = enclist.__getitem__
    return b''.join(map(encode, values))


def uridecode(uristring, encoding='utf-8', errors='strict'):
    """Decode a URI string or string component."""
    if isinstance(uristring, bytes):
        parts = uristring.split(b'%')
    else:
        parts = uristring.encode(encoding or 'ascii', errors).split(b'%')
    result = [parts[0]]
    append = result.append
    decode = _decoded.get
    for s in parts[1:]:
        append(decode(s[:2], b'%' + s[:2]))
        append(s[2:])
    if encoding is not None:
        return b''.join(result).decode(encoding, errors)
    else:
        return b''.join(result)
