from .const import UNRESERVED

try:
    from urllib import quote as _quote, unquote as _unquote
except ImportError:
    from urllib.parse import quote as _quote, unquote_to_bytes as _unquote


def uriencode(string, safe='', encoding='utf-8'):
    """Encode `string` using the codec registered for `encoding`,
    replacing any characters not in :const:`UNRESERVED` or `safe` with
    their corresponding percent-encodings.

    """
    return _quote(string.encode(encoding), UNRESERVED + safe)


def uridecode(string, encoding='utf-8'):
    """Replace any percent-encodings in `string`, and decode the resulting
    string using the codec registered for `encoding`.

    """
    return _unquote(string).decode(encoding)
