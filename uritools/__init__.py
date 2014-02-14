"""RFC 3986 compliant, Unicode-aware, scheme-agnostic replacement for
urlparse.

This module defines RFC 3986 compliant replacements for the most
commonly used functions of the Python Standard Library `urlparse`
module.
"""
from collections import namedtuple
import re

__version__ = '0.1.0'

# RFC 3986 2.2. Reserved Characters

GEN_DELIMS = ':/?#[]@'
"""General delimiter characters"""

SUB_DELIMS = "!$&'()*+,;="
"""Sub-component delimiter characters"""

RESERVED = GEN_DELIMS + SUB_DELIMS
"""Reserved characters"""

# RFC 3986 2.3. Unreserved Characters

UNRESERVED = (
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    'abcdefghijklmnopqrstuvwxyz'
    '0123456789'
    '_.-~'
)
"""Unreserved characters"""

# RFC 3986 Appendix B

RE = re.compile(r"""
(?:([^:/?#]+):)?  # scheme
(?://([^/?#]*))?  # authority
([^?#]*)          # path
(?:\?([^#]*))?    # query
(?:\#(.*))?       # fragment
""", flags=(re.VERBOSE))
"""Regular expression to split URIs into components."""


def urisplit(uri):
    """Split a URI string into a tuple with five components, according
    to a URI's general structure::

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
    """Combine the elements of a five-item iterable as returned by
    `urisplit()` into a URI string.

    """

    scheme, authority, path, query, fragment = parts

    # RFC 3986 3.: The scheme and path components are required, though
    # the path may be empty (no characters).
    #
    # We relax the requirement for presence of the scheme to allow for
    # URI references, but do not allow empty schemes, since these are
    # not recognized by the RE given in RFC 3986 Appendix B.
    if scheme == '':
        raise ValueError('URI scheme must not be empty')
    if path is None:
        raise ValueError('URI path must be present if empty')

    # RFC 3986 3.3.: If a URI contains an authority component, then
    # the path component must either be empty or begin with a slash
    # ("/") character.  If a URI does not contain an authority
    # component, then the path cannot begin with two slash characters
    # ("//").  In addition, a URI reference may be a relative-path
    # reference, in which case the first path segment cannot contain a
    # colon (":") character.
    if authority is not None and path and not path.startswith('/'):
        raise ValueError('Cannot use path %r with authority' % path)
    if authority is None and path.startswith('//'):
        raise ValueError('Cannot use path %r without authority' % path)
    if scheme is None and ':' in path.split('/', 1)[0]:
        raise ValueError('Cannot use path %r without scheme' % path)

    # Prevent some reserved characters within parts, so that for all
    # parts, uri: urisplit(uriunsplit(parts)) == parts and
    # uriunsplit(urisplit(uri)) == uri
    for part in zip(parts, (':/?#', '/?#', '?#', '#', '')):
        if part[0] and any(c in part[1] for c in part[0]):
            raise ValueError('Reserved character in %r' % part[0])

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
    scheme, authority, path, query, fragment = urisplit(uri)
    return (uriunsplit((scheme, authority, path, query, None)), fragment)


def uriencode(string, safe='', encoding='utf-8'):
    """Encode `string` using the codec registered for `encoding`,
    replacing any unreserved characters not in `safe` with their
    corresponding percent-encodings.

    """
    from urllib import quote
    return quote(string.encode(encoding), UNRESERVED + safe)


def uridecode(string, encoding='utf-8'):
    """Replace percent-encodings in `string`, and decode the resulting
    string using the codec registered for `encoding`."""
    from urllib import unquote
    return unquote(string).decode(encoding)


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

    if scheme is not None:
        scheme = uriencode(scheme, encoding='ascii')
    if authority is not None:
        authority = uriencode(authority, SUB_DELIMS + ':@', encoding)
    if path is not None:
        path = uriencode(path, SUB_DELIMS + ':@/', encoding)
    if query is not None:
        query = uriencode(query, SUB_DELIMS + ':@/?', encoding)
    if fragment is not None:
        fragment = uriencode(fragment, SUB_DELIMS + ':@/?', encoding)
    return uriunsplit((scheme, authority, path, query, fragment))


class SplitResult(namedtuple('SplitResult', 'scheme authority path query fragment')):
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
        else:
            if authority is not None:
                path = urinormpath(path)
            else:
                if not path:
                    path = self.path
                    if query is None:
                        query = self.query
                elif path.startswith('/'):
                    path = urinormpath(path)
                elif self.authority is not None and not self.path:
                    path = urinormpath('/' + path)
                else:
                    basepath = self.path[:self.path.rfind('/') + 1]
                    path = urinormpath(basepath + path)
                authority = self.authority
            scheme = self.scheme
        return SplitResult(scheme, authority, path, query, fragment)
