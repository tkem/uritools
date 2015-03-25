from __future__ import unicode_literals

import ipaddress
import itertools
import re

from collections import Iterable, Mapping

try:
    String = (basestring, bytearray)
except NameError:
    String = (str, bytes, bytearray)

from .const import SUB_DELIMS
from .parse import uriunsplit
from .encoding import uriencode

# RFC 3986 3.1: scheme = ALPHA *( ALPHA / DIGIT / "+" / "-" / "." )
SCHEME_RE = re.compile(br"\A[A-Za-z][A-Za-z0-9+.-]*\Z")

# RFC 3986 3.2: authority = [ userinfo "@" ] host [ ":" port ]
AUTHORITY_RE = re.compile(r"\A(?:(.*)@)?(.*?)(?::([0-9]*))?\Z")


def ifnone(a, b):
    return a if a is not None else b


def splitauth(authority, userinfo, host, port, encoding='utf-8'):
    if isinstance(authority, type('')):
        parts = AUTHORITY_RE.match(authority).groups()
    elif isinstance(authority, String):
        parts = AUTHORITY_RE.match(authority.decode(encoding)).groups()
    elif isinstance(authority, Iterable):
        _, _, _ = parts = authority
    else:
        raise TypeError('Invalid authority type')
    return itertools.starmap(ifnone, zip((userinfo, host, port), parts))


def ip_literal(address):
    if address.startswith('v'):
        raise ipaddress.AddressValueError('Address mechanism not supported')
    else:
        return b'[' + ipaddress.IPv6Address(address).compressed.encode() + b']'


def hoststr(host, encoding):
    if host.startswith('[') and host.endswith(']'):
        return ip_literal(host[1:-1])
    if host.startswith('[') or host.endswith(']'):
        raise ValueError('Invalid host subcomponent %r' % host)
    try:
        # check for IPv6 addresses as returned by SplitResult.gethost()
        return b'[' + ipaddress.IPv6Address(host).compressed.encode() + b']'
    except ValueError:
        return uriencode(host, SUB_DELIMS, encoding).lower()


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
               fragment=None, userinfo=None, host=None, port=None,
               delim=b'&', encoding='utf-8'):
    """Compose a URI string from its components.

    If `query` is a mapping object or a sequence of two-element
    tuples, it will be converted to a string of `key=value` pairs
    seperated by `delim`.

    """

    if path is None:
        raise ValueError('URI path component must be present if empty')
    if authority is not None:
        userinfo, host, port = splitauth(authority, userinfo, host, port, encoding)  # noqa
    if host is None and (userinfo is not None or port is not None):
        raise ValueError('URI host subcomponent must be present if empty')
    authority = b'' if host is not None else None

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
        s = uriencode(scheme, safe=b'+')
        if not SCHEME_RE.match(s):
            raise ValueError('Invalid scheme component %r' % scheme)
        scheme = s.lower()

    # RFC 3986 3.2.1: The user information, if present, is followed by
    # a commercial at-sign ("@") that delimits it from the host.
    if userinfo is not None:
        authority += uriencode(userinfo, SUB_DELIMS + b':', encoding) + b'@'

    # RFC 3986 3.2.3: Although host is case-insensitive, producers and
    # normalizers should use lowercase for registered names and
    # hexadecimal addresses for the sake of uniformity, while only
    # using uppercase letters for percent-encodings.
    if host is not None:
        if isinstance(host, ipaddress.IPv4Address):
            authority += host.compressed.encode()
        elif isinstance(host, ipaddress.IPv6Address):
            authority += b'[' + host.compressed.encode() + b']'
        elif isinstance(host, type('')):
            authority += hoststr(host, encoding)
        elif isinstance(host, String):
            authority += hoststr(host.decode(encoding), encoding)
        else:
            raise TypeError('Invalid host type')

    # RFC 3986 3.2.3: URI producers and normalizers should omit the
    # port component and its ":" delimiter if port is empty or if its
    # value would be the same as that of the scheme's default.
    if port is not None:
        if isinstance(port, type('')):
            port = port.encode(encoding)
        elif not isinstance(port, String):
            port = str(port).encode(encoding)  # handle int, etc.
        if not port:
            pass  # empty
        elif not port.isdigit():
            raise ValueError('Invalid port subcomponent %r', port)
        else:
            authority += b':' + port

    # RFC 3986 3.3: If a URI contains an authority component, then the
    # path component must either be empty or begin with a slash ("/")
    # character.  If a URI does not contain an authority component,
    # then the path cannot begin with two slash characters ("//").
    p = uriencode(path, SUB_DELIMS + b':@/', encoding)
    if authority is not None and p and not p.startswith(b'/'):
        raise ValueError('Invalid path %r with authority component' % path)
    if authority is None and p.startswith(b'//'):
        raise ValueError('Invalid path %r without authority component' % path)
    # RFC 3986 4.2: A path segment that contains a colon character
    # (e.g., "this:that") cannot be used as the first segment of a
    # relative-path reference, as it would be mistaken for a scheme
    # name.  Such a segment must be preceded by a dot-segment (e.g.,
    # "./this:that") to make a relative-path reference.
    if scheme is None and authority is None and b':' in p.partition(b'/')[0]:
        p = b'./' + p
    path = p

    # RFC 3986 3.4: The characters slash ("/") and question mark ("?")
    # may represent data within the query component.  Beware that some
    # older, erroneous implementations may not handle such data
    # correctly when it is used as the base URI for relative
    # references (Section 5.1), apparently because they fail to
    # distinguish query data from path data when looking for
    # hierarchical separators.  However, as query components are often
    # used to carry identifying information in the form of "key=value"
    # pairs and one frequently used value is a reference to another
    # URI, it is sometimes better for usability to avoid percent-
    # encoding those characters.
    if query is not None:
        if isinstance(query, String):
            query = uriencode(query, SUB_DELIMS + b':@/?', encoding)
        elif isinstance(query, Mapping):
            query = querydict(query, delim, encoding)
        elif isinstance(query, Iterable):
            query = querylist(query, delim, encoding)
        else:
            raise TypeError('Invalid query type')

    # RFC 3986 3.5: The characters slash ("/") and question mark ("?")
    # are allowed to represent data within the fragment identifier.
    # Beware that some older, erroneous implementations may not handle
    # this data correctly when it is used as the base URI for relative
    # references.
    if fragment is not None:
        fragment = uriencode(fragment, SUB_DELIMS + b':@/?', encoding)

    result = uriunsplit((scheme, authority, path, query, fragment))
    # FIXME: better way to handle this?
    return result if isinstance(result, str) else result.decode('ascii')
