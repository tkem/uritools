from string import hexdigits as _hex

from .chars import UNRESERVED


# RFC 3986 2.1: For consistency, URI producers and normalizers should
# use uppercase hexadecimal digits for all percent-encodings.
def _pctenc(byte):
    return ("%%%02X" % byte).encode()


_unreserved = frozenset(UNRESERVED.encode())

_encoded = {b"": [bytes([i]) if i in _unreserved else _pctenc(i) for i in range(256)]}

_decoded = {(a + b).encode(): bytes.fromhex(a + b) for a in _hex for b in _hex}


def uriencode(uristring, safe="", encoding="utf-8", errors="strict"):
    """Encode a URI string or string component."""
    if not isinstance(uristring, bytes):
        uristring = uristring.encode(encoding, errors)
    if not isinstance(safe, bytes):
        safe = safe.encode("ascii")
    try:
        encoded = _encoded[safe]
    except KeyError:
        encoded = _encoded[b""][:]
        for i in safe:
            encoded[i] = bytes([i])
        _encoded[safe] = encoded
    return b"".join(map(encoded.__getitem__, uristring))


def uridecode(uristring, encoding="utf-8", errors="strict"):
    """Decode a URI string or string component."""
    if not isinstance(uristring, bytes):
        uristring = uristring.encode(encoding or "ascii", errors)
    parts = uristring.split(b"%")
    result = [parts[0]]
    append = result.append
    decode = _decoded.get
    for s in parts[1:]:
        append(decode(s[:2], b"%" + s[:2]))
        append(s[2:])
    if encoding is not None:
        return b"".join(result).decode(encoding, errors)
    else:
        return b"".join(result)
