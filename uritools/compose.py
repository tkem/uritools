from __future__ import unicode_literals

import re

from collections import Iterable, Mapping

try:
    String = (basestring, bytearray)
except NameError:
    String = (str, bytes, bytearray)

from .const import SUB_DELIMS
from .parse import uriunsplit
from .encoding import uriencode
from .ipaddress import ip_address

# RFC 3986 3.1: scheme = ALPHA *( ALPHA / DIGIT / "+" / "-" / "." )
SCHEME_RE = re.compile(br"\A[A-Za-z][A-Za-z0-9+.-]*\Z")

# RFC 3986 3.2: authority = [ userinfo "@" ] host [ ":" port ]
AUTHORITY_RE = re.compile(r"\A(?:(.*)@)?(.*?)(?::([0-9]*))?\Z")


def decoder(encoding):
    def decode(obj):
        return obj.decode(encoding) if hasattr(obj, 'decode') else obj
    return decode


def splitauth(authority, encoding):
    if isinstance(authority, type('')):
        return AUTHORITY_RE.match(authority).groups()
    elif isinstance(authority, String):
        return AUTHORITY_RE.match(authority.decode(encoding)).groups()
    elif isinstance(authority, Iterable):
        return map(decoder(encoding), authority)
    else:
        raise TypeError('Invalid authority type')


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
        if isinstance(scheme, type('')):
            encoded_scheme = scheme.encode()
        else:
            encoded_scheme = scheme
        if SCHEME_RE.match(encoded_scheme):
            scheme = encoded_scheme.lower()
        else:
            raise ValueError('Invalid scheme %r' % scheme)

    if authority is not None:
        userinfo, host, port = splitauth(authority, encoding)
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
            raise ValueError('URI host component must be present if empty')
        elif host.startswith('[') and host.endswith(']'):
            authority += b'[' + ip_address(host[1:-1]).encode() + b']'
        elif host.startswith('[') or host.endswith(']'):
            raise ValueError('Invalid host %r' % host)
        else:
            try:
                authority += b'[' + ip_address(host).encode() + b']'
            except ValueError:
                authority += uriencode(host, SUB_DELIMS, encoding).lower()
        # RFC 3986 3.2.3: URI producers and normalizers should omit
        # the port component and its ":" delimiter if port is empty or
        # if its value would be the same as that of the scheme's
        # default.
        port = str(port).encode() if port is not None else b''
        if port.isdigit():
            authority += b':' + port
        elif port:
            raise ValueError('Invalid port %r' % port)

    # RFC 3986 3.3: If a URI contains an authority component, then the
    # path component must either be empty or begin with a slash ("/")
    # character.  If a URI does not contain an authority component,
    # then the path cannot begin with two slash characters ("//").  In
    # addition, a URI reference may be a relative-path reference, in
    # which case the first path segment cannot contain a colon (":")
    # character.
    if path is None:
        raise ValueError('URI path component must be present if empty')
    else:
        path = uriencode(path, SUB_DELIMS + b':@/', encoding)
    if authority is not None and path and not path.startswith(b'/'):
        raise ValueError('Invalid path %r with authority component' % path)
    if authority is None and path.startswith(b'//'):
        raise ValueError('Invalid path %r without authority component' % path)
    if scheme is None and authority is None and path.find(b':') < path.find(b'/'):  # noqa
        raise ValueError('Invalid relative-path reference %r' % path)

    if query is not None:
        if isinstance(query, String):
            query = uriencode(query, SUB_DELIMS + b':@/?', encoding)
        elif isinstance(query, Mapping):
            query = querydict(query, delim, encoding)
        elif isinstance(query, Iterable):
            query = querylist(query, delim, encoding)
        else:
            raise TypeError('Invalid query type')

    if fragment is not None:
        fragment = uriencode(fragment, SUB_DELIMS + b':@/?', encoding)

    return uriunsplit((scheme, authority, path, query, fragment))
