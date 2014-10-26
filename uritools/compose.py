from .const import SUB_DELIMS
from .parse import uriunsplit
from .encoding import uriencode

from collections import Iterable, Mapping

try:
    String = basestring
except NameError:
    String = (str, bytes, bytearray)

import re

# RFC 3986 3.2: scheme = ALPHA *( ALPHA / DIGIT / "+" / "-" / "." )
_SCHEME_RE = re.compile(r"\A[A-Z][A-Z0-9+.-]*\Z", flags=re.IGNORECASE)


def splitauth(authority):
    if authority is None:
        return (None, None, None)
    elif isinstance(authority, type('')):
        atsign, colon, digits = '@', ':', '0123456789'
    else:
        atsign, colon, digits = b'@', b':', b'0123456789'
    # RFC 3986 3.2: authority = [ userinfo "@" ] host [ ":" port ]
    parts = authority.partition(atsign)
    if parts[1]:
        userinfo, host = parts[0], parts[2]
    else:
        userinfo, host = None, parts[0]
    if host.rstrip(digits).endswith(colon):
        host, _, port = host.rpartition(colon)
    else:
        port = None
    return (userinfo, host, port)


def querylist(items, delim, encoding):
    safe = (SUB_DELIMS + b':@/?').replace(delim, b'')
    terms = []
    append = terms.append
    for key, value in items:
        name = uriencode(key, safe, encoding)
        if value is None:
            append(name)
        elif isinstance(value, String):
            append(name + b'=' + uriencode(value, safe, encoding))
        else:
            append(name + b'=' + uriencode(str(value), safe, encoding))
    return delim.join(terms)


def querydict(mapping, delim, encoding):
    items = []
    append = items.append
    extend = items.extend
    for key, value in mapping.items():
        if isinstance(value, Iterable) and not isinstance(value, String):
            extend([(key, v) for v in value])
        else:
            append((key, value))
    return querylist(items, delim, encoding)


def uricompose(scheme=None, authority=None, path='', query=None,
               fragment=None, delim=b'&', encoding='utf-8'):
    """Compose a URI string from its components.

    If `query` is a mapping object or a sequence of two-element
    tuples, it will be converted to a string of `key=value` pairs
    seperated by `delim`.

    """

    # RFC 3986 3.1: Scheme names consist of a sequence of characters
    # beginning with a letter and followed by any combination of
    # letters, digits, plus ("+"), period ("."), or hyphen ("-").
    # Although schemes are case-insensitive, the canonical form is
    # lowercase and documents that specify schemes must do so with
    # lowercase letters.  An implementation should accept uppercase
    # letters as equivalent to lowercase in scheme names (e.g., allow
    # "HTTP" as well as "http") for the sake of robustness but should
    # only produce lowercase scheme names for consistency.
    if scheme is not None:
        if not _SCHEME_RE.match(scheme):
            raise ValueError('Invalid scheme: %r' % scheme)
        scheme = scheme.lower().encode()

    if authority is not None:
        if isinstance(authority, String):
            userinfo, host, port = splitauth(authority)
        else:
            userinfo, host, port = authority
        # RFC 3986 3.2.1: The user information, if present, is
        # followed by a commercial at-sign ("@") that delimits it from
        # the host.
        if userinfo is not None:
            authority = uriencode(userinfo, SUB_DELIMS + b':', encoding) + b'@'
        else:
            authority = b''
        # RFC 3986 3.2.3: Although host is case-insensitive, producers
        # and normalizers should use lowercase for registered names
        # and hexadecimal addresses for the sake of uniformity, while
        # only using uppercase letters for percent-encodings.
        if host is None:
            raise ValueError('Host subcomponent must be present if empty')
        host = host.lower()
        if host.startswith('[') and host.endswith(']'):
            authority += uriencode(host, SUB_DELIMS + b':')  # TODO: check IPv6
        #elif _IPV6_ADDRESS_RE.match(host):
        #    authority += b'[' + uriencode(host, SUB_DELIMS + b':') + b']'
        else:
            authority += uriencode(host, SUB_DELIMS, encoding)
        # RFC 3986 3.2.3: URI producers and normalizers should omit
        # the port component and its ":" delimiter if port is empty or
        # if its value would be the same as that of the scheme's
        # default.
        port = str(port).encode(encoding) if port is not None else b''
        if port.isdigit():
            authority += b':' + port
        elif port:
            raise ValueError('Non-decimal port: %s' % port)

    # RFC 3986 3.3: If a URI contains an authority component, then the
    # path component must either be empty or begin with a slash ("/")
    # character.  If a URI does not contain an authority component,
    # then the path cannot begin with two slash characters ("//").  In
    # addition, a URI reference may be a relative-path reference, in
    # which case the first path segment cannot contain a colon (":")
    # character.
    if path is None:
        raise ValueError('URI path component must be present if empty')
    if authority is not None and path and not path.startswith('/'):
        raise ValueError('Invalid path %r with authority component' % path)
    if authority is None and path.startswith('//'):
        raise ValueError('Invalid path %r without authority component' % path)
    if scheme is None and authority is None and ':' in path.split('/', 1)[0]:
        raise ValueError('Invalid path %r without scheme component' % path)
    path = uriencode(path, SUB_DELIMS + b':@/', encoding)

    if query is not None:
        if isinstance(query, String):
            query = uriencode(query, SUB_DELIMS + b':@/?', encoding)
        elif isinstance(query, Mapping):
            query = querydict(query, delim, encoding)
        else:
            query = querylist(query, delim, encoding)

    if fragment:
        fragment = uriencode(fragment, SUB_DELIMS + b':@/?', encoding)

    return uriunsplit((scheme, authority, path, query, fragment))
