"""RFC 3986 compliant, Unicode-aware, scheme-agnostic replacement for
urlparse.

This module defines RFC 3986 compliant replacements for the most
commonly used functions of the Python 2.7 Standard Library
:mod:`urlparse` module.

"""
import collections
import re

try:
    from urllib import quote as _quote, unquote as _unquote
except ImportError:
    from urllib.parse import quote as _quote, unquote_to_bytes as _unquote

try:
    basestring = basestring
except NameError:
    basestring = str

__version__ = '0.5.1'

RE = re.compile(r"""
(?:(?P<scheme>[^:/?#]+):)?      # scheme
(?://(?P<authority>[^/?#]*))?   # authority
(?P<path>[^?#]*)                # path
(?:\?(?P<query>[^#]*))?         # query
(?:\#(?P<fragment>.*))?         # fragment
""", flags=(re.VERBOSE))
"""Regular expression for splitting a well-formed URI into its
components, as specified in RFC 3986 Appendix B.

"""

GEN_DELIMS = ':/?#[]@'
"""General delimiting characters specified in RFC 3986."""

SUB_DELIMS = "!$&'()*+,;="
"""Subcomponent delimiting characters specified in RFC 3986."""

RESERVED = GEN_DELIMS + SUB_DELIMS
"""Reserved characters specified in RFC 3986."""

UNRESERVED = (
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    'abcdefghijklmnopqrstuvwxyz'
    '0123456789'
    '_.-~'
)
"""Unreserved characters specified in RFC 3986."""

_URI_COMPONENTS = ('scheme', 'authority', 'path', 'query', 'fragment')

_SCHEME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9.+-]*$")

_AUTHORITY_RE = re.compile(r"""
(?:(.*)\@)?     # userinfo
(.*?)           # host -- FIXME: lookahead?
(?:\:(\d+))?    # port
$
""", flags=(re.VERBOSE))


def _queryencode(query, delim, sep, encoding):
    if not delim:
        delim = ''
    if not sep:
        sep = ''
    # TODO: provide our own quote/unquote implementation?
    safe = (SUB_DELIMS + ':@/?').replace(delim, '').replace(sep, '')
    items = []
    for item in query:
        if isinstance(item, basestring):
            parts = (uriencode(item, safe, encoding), )
        else:
            parts = (uriencode(part, safe, encoding) for part in item)
        items.append(sep.join(parts))
    return delim.join(items)


def urisplit(string):
    """Split a well-formed URI string into a tuple with five components
    corresponding to a URI's general structure::

      <scheme>://<authority>/<path>?<query>#<fragment>

    The return value is an instance of a subclass of
    :class:`collections.namedtuple` with the following read-only
    attributes:

    +-------------------+-------+---------------------------------------------+
    | Attribute         | Index | Value                                       |
    +===================+=======+=============================================+
    | :attr:`scheme`    | 0     | URI scheme, or :const:`None` if not present |
    +-------------------+-------+---------------------------------------------+
    | :attr:`authority` | 1     | Authority component,                        |
    |                   |       | or :const:`None` if not present             |
    +-------------------+-------+---------------------------------------------+
    | :attr:`path`      | 2     | Path component, always present but may be   |
    |                   |       | empty                                       |
    +-------------------+-------+---------------------------------------------+
    | :attr:`query`     | 3     | Query component,                            |
    |                   |       | or :const:`None` if not present             |
    +-------------------+-------+---------------------------------------------+
    | :attr:`fragment`  | 4     | Fragment identifier,                        |
    |                   |       | or :const:`None` if not present             |
    +-------------------+-------+---------------------------------------------+
    | :attr:`userinfo`  |       | Userinfo subcomponent of authority,         |
    |                   |       | or :const:`None` if not present             |
    +-------------------+-------+---------------------------------------------+
    | :attr:`host`      |       | Host subcomponent of authority,             |
    |                   |       | or :const:`None` if not present             |
    +-------------------+-------+---------------------------------------------+
    | :attr:`port`      |       | Port subcomponent of authority as an        |
    |                   |       | :class:`int`, or :const:`None` if not       |
    |                   |       | present                                     |
    +-------------------+-------+---------------------------------------------+

    """
    try:
        return SplitResult(*RE.match(string).groups())
    except TypeError:
        # Python 3: handle string as bytes
        groups = RE.match(string.decode('ascii')).groups()
        groups = (None if g is None else g.encode('ascii') for g in groups)
        return SplitResult(*groups)


def uriunsplit(parts):
    """Combine the elements of a five-item iterable into a URI string.

    """
    scheme, authority, path, query, fragment = parts

    # RFC 3986 5.3. Component Recomposition
    try:
        result = ''
        if scheme is not None:
            result += scheme + ':'
        if authority is not None:
            result += '//' + authority
        result += path
        if query is not None:
            result += '?' + query
        if fragment is not None:
            result += '#' + fragment
        return result
    except TypeError:
        # Python 3: handle parts as bytes
        parts = (None if p is None else p.decode('ascii') for p in parts)
        return uriunsplit(parts).encode('ascii')


def urijoin(base, ref, strict=False):
    """Convert a URI reference relative to a base URI to its target
    URI string."""
    return uriunsplit(urisplit(base).transform(ref, strict))


def uridefrag(string):
    """Remove an existing fragment component from a URI string.

    The return value is an instance of a subclass of
    :class:`collections.namedtuple` with the following read-only
    attributes:

    +-------------------+-------+---------------------------------------------+
    | Attribute         | Index | Value                                       |
    +===================+=======+=============================================+
    | :attr:`base`      | 0     | The absoulte URI or relative URI reference  |
    |                   |       | without the fragment identifier             |
    +-------------------+-------+---------------------------------------------+
    | :attr:`fragment`  | 1     | The fragment identifier,                    |
    |                   |       | or :const:`None` if not present             |
    +-------------------+-------+---------------------------------------------+

    """
    try:
        parts = string.partition('#')
    except TypeError:
        # Python 3: handle string as bytes
        parts = string.partition(b'#')
    if parts[1]:
        return DefragResult(parts[0], parts[2])
    else:
        return DefragResult(parts[0], None)


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


def urinormpath(path):
    """Remove '.' and '..' path segments from a URI path."""

    # RFC 3986 5.2.4. Remove Dot Segments
    out = []
    for s in path.split('/'):
        if s == '.':
            continue
        elif s != '..':
            out.append(s)
        elif out:
            out.pop()
    # Fix leading/trailing slashes
    if path.startswith('/') and (not out or out[0]):
        out.insert(0, '')
    if path.endswith('/.') or path.endswith('/..'):
        out.append('')
    return '/'.join(out)


def uricompose(scheme=None, authority=None, path='', query=None,
               fragment=None, delim='&', querysep='=',
               encoding='utf-8'):
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
        # TODO: check authority is well-formed, IPv6 support
        authority = uriencode(authority, SUB_DELIMS + ':@', encoding)

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
        raise ValueError('Invalid path %r with authority' % path)
    if authority is None and path.startswith('//'):
        raise ValueError('Invalid path %r without authority' % path)
    if scheme is None and authority is None and ':' in path.split('/', 1)[0]:
        raise ValueError('Invalid path %r without scheme' % path)
    path = uriencode(path, SUB_DELIMS + ':@/', encoding)

    if query is not None:
        if isinstance(query, basestring):
            query = uriencode(query, SUB_DELIMS + ':@/?', encoding)
        elif hasattr(query, 'items'):
            query = _queryencode(query.items(), delim, querysep, encoding)
        else:
            query = _queryencode(query, delim, querysep, encoding)

    if fragment:
        fragment = uriencode(fragment, SUB_DELIMS + ':@/?', encoding)

    return uriunsplit((scheme, authority, path, query, fragment))


class SplitResult(collections.namedtuple('SplitResult', _URI_COMPONENTS)):
    """Class to hold :func:`urisplit` results."""

    @property
    def _splitauth(self):
        if self.authority is None:
            return (None, None, None)
        else:
            return _AUTHORITY_RE.match(self.authority).groups()

    @property
    def userinfo(self):
        return self._splitauth[0]

    @property
    def host(self):
        return self._splitauth[1]

    @property
    def port(self):
        port = self._splitauth[2]
        return int(port, 10) if port is not None else None

    def geturi(self):
        """Return the re-combined version of the original URI as a string."""
        return uriunsplit(self)

    def getscheme(self, default=None):
        """Return the URI scheme in canonical (lowercase) form, or `default`
        if the original URI did not contain a scheme component.  Raise
        a :class:`ValueError` if the scheme is not well-formed.

        """
        if self.scheme is None:
            return default
        try:
            scheme = self.scheme.decode('ascii')
        except AttributeError:
            scheme = self.scheme
        if not _SCHEME_RE.match(scheme):
            raise ValueError('Invalid scheme: %r' % scheme)
        return scheme.lower()

    def getauthority(self, default=None, encoding='utf-8'):
        """Return the decoded URI authority, or `default` if the original URI
        did not contain an authority component.

        """
        if self.authority is None:
            return default
        return uridecode(self.authority, encoding)

    def getpath(self, encoding='utf-8'):
        """Return the decoded URI path."""
        return uridecode(self.path, encoding)

    def getquery(self, default=None, encoding='utf-8'):
        """Return the decoded query string, or `default` if the original URI
        did not contain a query component.

        """
        if self.query is None:
            return default
        return uridecode(self.query, encoding)

    def getfragment(self, default=None, encoding='utf-8'):
        """Return the decoded fragment identifier, or `default` if the
        original URI did not contain a fragment component.

        """
        if self.fragment is None:
            return default
        return uridecode(self.fragment, encoding)

    def getuserinfo(self, default=None, encoding='utf-8'):
        """Return the decoded userinfo subcomponent of the URI authority, or
        `default` if the original URI did not contain a userinfo
        field.

        """
        if self.userinfo is None:
            return default
        return uridecode(self.userinfo, encoding)

    def gethost(self, default=None, encoding='utf-8'):
        """Return the decoded host subcomponent of the URI authority, or
        `default` if the original URI did not contain a host.

        If the host represents an internationalized domain name
        intended for resolution via DNS, the :const:`'idna'` encoding
        must be specified to return a Unicode domain name.

        """
        if self.host is None:
            return default
        return uridecode(self.host, encoding)

    def getport(self, default=None):
        """Return the port subcomponent of the URI authority as an
        :class:`int`, or `default` if the original URI did not contain
        a port.

        """
        return self.port if self.port is not None else default

    def getaddrinfo(self, family=0, type=0, proto=0, flags=0):
        """Translate the host and port subcomponents of the URI authority into
        a sequence of 5-tuples as reported by
        :func:`socket.getaddrinfo`.

        If the URI authority does not contain a port subcomponent, the
        URI scheme is interpreted as a service name.  The optional
        `family`, `type`, `proto` and `flags` arguments are passed to
        :func:`socket.getaddrinfo` as-is,

        """
        import socket
        host = self.host
        port = self.port or self.scheme
        return socket.getaddrinfo(host, port, family, type, proto, flags)

    def getquerylist(self, delims=';&', sep='=', encoding='utf-8'):
        """Split the query string into individual components using the
        delimiter characters in `delims`.

        If `sep` is not empty, split each component at the first
        occurence of `sep` and return a list of decoded `(name,
        value)` pairs.  If `sep` is not found, `value` becomes
        :const:`None`.

        If `sep` is :const:`None` or empty, return the list of decoded
        query components.
        """
        qsl = [self.query] if self.query else []
        for delim in delims:
            qsl = [s for qs in qsl for s in qs.split(delim) if s]
        if not sep:
            return [uridecode(qs, encoding) for qs in qsl]
        items = []
        for qs in qsl:
            parts = qs.partition(sep)
            name = uridecode(parts[0], encoding)
            value = uridecode(parts[2], encoding) if parts[1] else None
            items.append((name, value))
        return items

    def getquerydict(self, delims=';&', sep='=', encoding='utf-8'):
        """Split the query string into individual components using the
        delimiter characters in `delims`, and return a dictionary of
        query parameters.

        The dictionary keys are the unique decoded query parameter
        names, and the values are lists of decoded values for each
        name.  Parameter names and values are seperated by `sep`.
        """
        dict = collections.defaultdict(list)
        for name, value in self.getquerylist(delims, sep, encoding):
            dict[name].append(value)
        return dict

    def transform(self, ref, strict=False):
        """Convert a URI reference relative to `self` into a
        :class:`SplitResult` representing its target.

        """
        scheme, authority, path, query, fragment = urisplit(ref)

        # RFC 3986 5.2.2. Transform References
        if scheme is not None and (strict or scheme != self.scheme):
            path = urinormpath(path)
            return SplitResult(scheme, authority, path, query, fragment)
        if authority is not None:
            path = urinormpath(path)
            return SplitResult(self.scheme, authority, path, query, fragment)
        if not path:
            path = self.path
            if query is None:
                query = self.query
        elif path.startswith('/'):
            path = urinormpath(path)
        elif self.authority is not None and not self.path:
            path = urinormpath('/' + path)
        else:
            path = urinormpath(self.path[:self.path.rfind('/') + 1] + path)
        return SplitResult(self.scheme, self.authority, path, query, fragment)


class DefragResult(collections.namedtuple('DefragResult', 'base fragment')):
    """Class to hold :func:`uridefrag` results."""

    def geturi(self):
        """Return the re-combined version of the original URI as a string."""
        if self.fragment is not None:
            try:
                return self.base + '#' + self.fragment
            except TypeError:
                # Python 3: handle string as bytes
                return self.base + b'#' + self.fragment
        else:
            return self.base

    def getbase(self, encoding='utf-8'):
        """Return the decoded absolute URI or relative URI reference without
        the fragment.

        """
        return uridecode(self.base, encoding)

    def getfragment(self, default=None, encoding='utf-8'):
        """Return the decoded fragment identifier, or `default` if the
        original URI did not contain a fragment component.

        """
        if self.fragment is None:
            return default
        return uridecode(self.fragment, encoding)
