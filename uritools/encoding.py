from .const import UNRESERVED
from .util import byte, iterbytes, unicode

from string import hexdigits


# RFC 3986 2.1: For consistency, URI producers and normalizers should
# use uppercase hexadecimal digits for all percent-encodings.
def encode(byte):
    return ('%%%02X' % byte).encode()

try:
    fromhex = bytes.fromhex
except AttributeError:
    fromhex = lambda x: chr(int(x, 16))

encoded = {
    b'': [byte(i) if byte(i) in UNRESERVED else encode(i) for i in range(256)]
}

decoded = {
    (a + b).encode(): fromhex(a + b) for a in hexdigits for b in hexdigits
}


def uridecode(string, encoding='utf-8'):
    """Replace any percent-encodings in `string`, and decode the resulting
    string using the codec registered for `encoding`.

    `string` may be a Unicode or byte string.

    """
    if isinstance(string, unicode):
        string = string.encode(encoding)
    parts = string.split(b'%')
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

    `string` may be a Unicode or byte string, while `safe` must be a
    bytes-like object containg ASCII characters only.

    """
    if isinstance(string, unicode):
        string = string.encode(encoding)
    try:
        encode = encoded[safe]
    except KeyError:
        encode = encoded[b''][:]
        for i in iterbytes(safe):
            encode[i] = byte(i)
        encoded[safe] = encode
    return b''.join(map(encode.__getitem__, iterbytes(string)))
