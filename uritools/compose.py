from .const import SUB_DELIMS
from .encoding import uriencode
from .regex import _SCHEME_RE, _AUTHORITY_RE, _IPV6_ADDRESS_RE
from .split import uriunsplit

try:
    basestring = basestring
except NameError:
    basestring = str


def _queryencode(query, delim, encoding):
    if not delim:
        delim = ''
    # TODO: provide our own quote/unquote implementation?
    safe = (SUB_DELIMS + ':@/?').replace(delim, '')
    items = []
    for item in query:
        if isinstance(item, basestring):
            parts = (uriencode(item, safe, encoding), )
        else:
            parts = (uriencode(part, safe, encoding) for part in item)
        items.append('='.join(parts))
    return delim.join(items)


def uricompose(scheme=None, authority=None, path='', query=None,
               fragment=None, delim='&', encoding='utf-8'):
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
        scheme = scheme.lower()

    if authority is not None:
        if isinstance(authority, basestring):
            userinfo, host, port = _AUTHORITY_RE.match(authority).groups()
        else:
            userinfo, host, port = authority
        # RFC 3986 3.2.1: The user information, if present, is
        # followed by a commercial at-sign ("@") that delimits it from
        # the host.
        if userinfo is not None:
            authority = uriencode(userinfo, SUB_DELIMS + ':', encoding) + '@'
        else:
            authority = ''
        # RFC 3986 3.2.3: Although host is case-insensitive, producers
        # and normalizers should use lowercase for registered names
        # and hexadecimal addresses for the sake of uniformity, while
        # only using uppercase letters for percent-encodings.
        if host is None:
            raise ValueError('Host subcomponent must be present if empty')
        host = host.lower()
        if host.startswith('[') and host.endswith(']'):
            authority += host  # TODO: check IPv6
        elif _IPV6_ADDRESS_RE.match(host):
            authority += '[' + host + ']'
        else:
            authority += uriencode(host, SUB_DELIMS, encoding)
        # RFC 3986 3.2.3: URI producers and normalizers should omit
        # the port component and its ":" delimiter if port is empty or
        # if its value would be the same as that of the scheme's
        # default.
        port = str(port) if port is not None else ''
        if port.isdigit():
            authority += ':' + port
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
    path = uriencode(path, SUB_DELIMS + ':@/', encoding)

    if query is not None:
        if isinstance(query, basestring):
            query = uriencode(query, SUB_DELIMS + ':@/?', encoding)
        elif hasattr(query, 'items'):
            query = _queryencode(query.items(), delim, encoding)
        else:
            query = _queryencode(query, delim, encoding)

    if fragment:
        fragment = uriencode(fragment, SUB_DELIMS + ':@/?', encoding)

    return uriunsplit((scheme, authority, path, query, fragment))
