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


def uridecode(string, encoding='utf-8'):
    """Replace any percent-encodings in `string`, and return a decoded
    version of the string, using the codec registered for `encoding`.

    """
    try:
        # FIXME: have to explicitly convert to bytes in Python 2.7 (???)
        parts = memoryview(string).tobytes().split(b'%')
    except TypeError:
        parts = string.encode(encoding).split(b'%')
    result = [parts[0]]
    append = result.append
    decode = decoded.get
    for s in parts[1:]:
        append(decode(s[:2], b'%' + s[:2]))
        append(s[2:])
    return b''.join(result).decode(encoding)


def uriencode(string, safe=b'', encoding='utf-8'):
    """Encode `string` using the codec registered for `encoding`,
    replacing any characters not in :const:`UNRESERVED` or `safe` with
    their corresponding percent-encodings.

    """
    try:
        bytelist = memoryview(string).tolist()
    except TypeError:
        bytelist = memoryview(string.encode(encoding)).tolist()
    try:
        encode = encoded[safe].__getitem__
    except KeyError:
        enclist = encoded[b''][:]
        for i in memoryview(safe).tolist():
            enclist[i] = fromint(i)
        encoded[safe] = enclist
        encode = enclist.__getitem__
    return b''.join(map(encode, bytelist))
