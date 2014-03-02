"""RFC 3986 compliant, Unicode-aware, scheme-agnostic replacement for
urlparse.

This module defines RFC 3986 compliant replacements for the most
commonly used functions of the Python Standard Library :mod:`urlparse`
module.

"""
import collections
import re
import urllib

__version__ = '0.3.0'

RE = re.compile(r"""
(?:(?P<scheme>[^:/?#]+):)?      # scheme
(?://(?P<authority>[^/?#]*))?   # authority
(?P<path>[^?#]*)                # path
(?:\?(?P<query>[^#]*))?         # query
(?:\#(?P<fragment>.*))?         # fragment
""", flags=(re.VERBOSE))
"""Regular expression for splitting a well-formed URI into its
components as specified in RFC 3986 Appendix B.

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
    | :attr:`port`      |       | Port subcomponent of authority,             |
    |                   |       | or :const:`None` if not present             |
    +-------------------+-------+---------------------------------------------+

    """
    return SplitResult(*RE.match(string).groups())


def uriunsplit(parts):
    """Combine the elements of a five-item iterable into a URI string.

    """
    scheme, authority, path, query, fragment = parts

    # RFC 3986 5.3. Component Recomposition
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
    parts = string.partition('#')
    if parts[1]:
        return DefragResult(parts[0], parts[2])
    else:
        return DefragResult(parts[0], None)


def uriencode(string, safe='', encoding='utf-8'):
    """Encode `string` using the codec registered for `encoding`,
    replacing any characters not in :const:`UNRESERVED` or `safe` with
    their corresponding percent-encodings.

    """
    return urllib.quote(string.encode(encoding), UNRESERVED + safe)


def uridecode(string, encoding='utf-8'):
    """Replace any percent-encodings in `string`, and decode the resulting
    string using the codec registered for `encoding`.

    """
    return urllib.unquote(string).decode(encoding)


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
               fragment=None, encoding='utf-8'):
    """Compose a URI string from its components."""

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

    # TODO querylist, querydict
    if query:
        query = uriencode(query, SUB_DELIMS + ':@/?', encoding)

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
        return self._splitauth[2]

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
        if not _SCHEME_RE.match(self.scheme):
            raise ValueError('Invalid scheme: %r' % self.scheme)
        return self.scheme.lower()

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
        return int(self.port, 10) if self.port is not None else default

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
            return self.base + '#' + self.fragment
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
