"""RFC 3986 compliant, Unicode-aware, scheme-agnostic replacement for
urlparse.

This module defines RFC 3986 compliant replacements for the most
commonly used functions of the Python Standard Library `urlparse`
module.
"""
from collections import namedtuple
import re
import urllib

__version__ = '0.2.0'

RE = re.compile(r"""
(?:(?P<scheme>[^:/?#]+):)?      # scheme
(?://(?P<authority>[^/?#]*))?   # authority
(?P<path>[^?#]*)                # path
(?:\?(?P<query>[^#]*))?         # query
(?:\#(?P<fragment>.*))?         # fragment
""", flags=(re.VERBOSE))
"""Regular expression for splitting a well-formed URI into its
components.

"""

GEN_DELIMS = ':/?#[]@'
"""General delimiter characters."""

SUB_DELIMS = "!$&'()*+,;="
"""Sub-component delimiter characters."""

RESERVED = GEN_DELIMS + SUB_DELIMS
"""Reserved characters."""

UNRESERVED = (
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    'abcdefghijklmnopqrstuvwxyz'
    '0123456789'
    '_.-~'
)
"""Unreserved characters."""

_URI_COMPONENTS = ('scheme', 'authority', 'path', 'query', 'fragment')

_SCHEME_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9.+-]*$")


def urisplit(uri):
    """Split a well-formed URI string into a tuple with five components,
    according to a URI's general structure::

      <scheme>://<authority>/<path>?<query>#<fragment>

    The return value is a named tuple with the following fields:

    +-------+-------------+-------------------------------------------------+
    | Index | Attribute   | Value                                           |
    +=======+=============+=================================================+
    | 0     | `scheme`    | URI scheme or `None` if not present             |
    +-------+-------------+-------------------------------------------------+
    | 1     | `authority` | authority component or `None` if not present    |
    +-------+-------------+-------------------------------------------------+
    | 2     | `path`      | path component, always present but may be empty |
    +-------+-------------+-------------------------------------------------+
    | 3     | `query`     | query component or `None` if not present        |
    +-------+-------------+-------------------------------------------------+
    | 4     | `fragment`  | fragment component or `None` if not present     |
    +-------+-------------+-------------------------------------------------+

    """
    return SplitResult(*RE.match(uri).groups())


def uriunsplit(parts):
    """Combine the elements of a five-item iterable into a URI string.

    """
    scheme, authority, path, query, fragment = parts

    if path is None:
        raise ValueError('URI path component must be present if empty')

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


def uridefrag(uri):
    """Remove an existing fragment from a URI string.

    Return a tuple of the defragmented URI and the fragment.  If `uri`
    contains no fragment, the second element is `None`.

    """
    if '#' in uri:
        return DefragResult(*uri.split('#', 1))
    else:
        return DefragResult(uri, None)


def uriencode(string, safe='', encoding='utf-8'):
    """Encode `string` using the codec registered for `encoding`,
    replacing any characters not in `UNRESERVED` or `safe` with their
    corresponding percent-encodings.

    """
    return urllib.quote(string.encode(encoding), UNRESERVED + safe)


def uridecode(string, encoding='utf-8'):
    """Replace percent-encodings in `string`, and decode the resulting
    string using the codec registered for `encoding`."""
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
    if path.startswith('/') and out[0] != '':
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
            raise ValueError('Invalid scheme %r' % scheme)
        scheme = scheme.lower()

    if authority is not None:
        # TODO: check authority is well-formed, allow '[]' for IPv6
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
        # TODO: encode ':' only in first path segment
        path = uriencode(path, SUB_DELIMS + '@/', encoding)
    else:
        path = uriencode(path, SUB_DELIMS + ':@/', encoding)

    # TODO querylist, querydict
    if query:
        query = uriencode(query, SUB_DELIMS + ':@/?', encoding)

    if fragment:
        fragment = uriencode(fragment, SUB_DELIMS + ':@/?', encoding)
    return uriunsplit((scheme, authority, path, query, fragment))


class SplitResult(namedtuple('SplitResult', _URI_COMPONENTS)):
    """Extend `namedtuple` to hold `urisplit()` results."""

    def geturi(self):
        """Return the re-combined version of the original URI as a string."""
        return uriunsplit(self)

    def transform(self, ref, strict=False):
        """Convert a URI reference relative to `self` into a `SplitResult`
        representing its target.

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


class DefragResult(namedtuple('DefragResult', 'defrag fragment')):
    """Extend `namedtuple` to hold `uridefrag()` results."""

    def geturi(self):
        """Return the re-combined version of the original URI as a string."""
        if self.fragment is not None:
            return self.defrag + '#' + self.fragment
        else:
            return self.defrag
