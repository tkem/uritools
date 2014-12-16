from .const import UNRESERVED
from string import hexdigits

try:
    fromhex = bytes.fromhex
except AttributeError:
    fromhex = lambda x: chr(int(x, 16))
if isinstance(chr(0), bytes):
    fromint = chr
else:
    fromint = lambda x: bytes([x])
unreserved = frozenset(memoryview(UNRESERVED).tolist())


# RFC 3986 2.1: For consistency, URI producers and normalizers should
# use uppercase hexadecimal digits for all percent-encodings.
def pctenc(byte):
    return ('%%%02X' % byte).encode()

encoded = {
    b'': [fromint(i) if i in unreserved else pctenc(i) for i in range(256)]
}

decoded = {
    (a + b).encode(): fromhex(a + b) for a in hexdigits for b in hexdigits
}


def uridecode(obj, encoding='utf-8', errors='strict'):
    """Decode a URI string or bytes-like object."""
    try:
        parts = memoryview(obj).tobytes().split(b'%')
    except TypeError:
        parts = obj.encode(encoding or 'ascii', errors).split(b'%')
    result = [parts[0]]
    append = result.append
    decode = decoded.get
    for s in parts[1:]:
        append(decode(s[:2], b'%' + s[:2]))
        append(s[2:])
    if encoding is not None:
        return b''.join(result).decode(encoding, errors)
    else:
        return b''.join(result)


def uriencode(obj, safe=b'', encoding='utf-8', errors='strict'):
    """Encode a URI string or bytes-like object."""
    try:
        bytelist = memoryview(obj).tolist()
    except TypeError:
        bytelist = memoryview(obj.encode(encoding, errors)).tolist()
    try:
        encode = encoded[safe].__getitem__
    except KeyError:
        enclist = encoded[b''][:]
        for i in memoryview(safe).tolist():
            enclist[i] = fromint(i)
        encoded[safe] = enclist
        encode = enclist.__getitem__
    return b''.join(map(encode, bytelist))
