"""RFC 3986 compliant, Unicode-aware, scheme-agnostic replacement for
urlparse.

This module defines fully RFC 3986 compliant replacements for the most
commonly used functions of the Python Standard Library `urlparse`
module.
"""
from collections import namedtuple
import re

__version__ = '0.1.0'

# RFC 3986: 2.2. Reserved Characters

GEN_DELIMS = ':/?#[]@'
"""General delimiter characters"""

SUB_DELIMS = "!$&'()*+,;="
"""Sub-component delimiter characters"""

RESERVED = GEN_DELIMS + SUB_DELIMS
"""Reserved characters"""

# RFC 3986: 2.3. Unreserved Characters

UNRESERVED = (
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    'abcdefghijklmnopqrstuvwxyz'
    '0123456789'
    '_.-~'
)
"""Unreserved characters"""

# RFC 3986: Appendix B

RE = re.compile(r"""
(?:([^:/?#]+):)?  # scheme
(?://([^/?#]*))?  # authority
([^?#]*)          # path
(?:\?([^#]*))?    # query
(?:\#(.*))?       # fragment
""", flags=(re.VERBOSE))
"""Regular expression to split URIs into components."""


def uriencode(string, safe='', encoding='utf-8'):
    """Encode `string` using the codec registered for `encoding`, and
    replace reserved characters with percent-encodings."""
    from urllib import quote
    return quote(string.encode(encoding), UNRESERVED + safe)


def uridecode(string, encoding='utf-8'):
    """Replace percent-escapes in `string`, and decode the resulting
    string using the codec registered for `encoding`."""
    from urllib import unquote
    return unquote(string).decode(encoding)


def urinormpath(path):
    """Remove '.' and '..' path segments from a URI path."""

    # see RFC 3986 5.2.4. Remove Dot Segments
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


class SplitResult(namedtuple('SplitResult', 'scheme authority path query fragment')):
    """Extend :class:`namedtuple` to hold :func:`urisplit` results."""

    def geturi(self):
        """Return the re-combined version of the original URL as a string."""
        return uriunsplit(self)

    def transform(self, ref, strict=False):
        """Convert a URI reference relative to `self` into a
        five-element tuple representing its target."""
        scheme, authority, path, query, fragment = urisplit(ref)

        # see RFC 3986 5.2.2 Transform References
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


def urisplit(uri):
    """Split a URI string into a named tuple with five components::

      <scheme>://<authority>/<path>?<query>#<fragment>

    The returned object is an instance of `SplitResult`.

    """
    return SplitResult(*RE.match(uri).groups())


def uriunsplit(parts):
    """Combine the elements of a tuple as returned by `urisplit()` into a
    complete URI as a string."""

    # see RFC 3986 5.3 Component Recomposition
    scheme, authority, path, query, fragment = parts
    result = ''

    if scheme:
        if any(c in ':/?#' for c in scheme):
            raise ValueError('Reserved character in %r' % scheme)
        result += scheme + ':'

    if authority is not None:
        if any(c in '/?#' for c in authority):
            raise ValueError('Reserved character in %r' % authority)
        result += '//' + authority

    if path is None:
        raise ValueError('URI path must be present if empty')
    if any(c in '?#' for c in path):
        raise ValueError('Reserved character in %r' % path)

    # RFC 3986 3.3: If a URI contains an authority component, then the
    # path component must either be empty or begin with a slash ("/")
    # character.  If a URI does not contain an authority component,
    # then the path cannot begin with two slash characters ("//").  In
    # addition, a URI reference may be a relative-path reference, in
    # which case the first path segment cannot contain a colon (":")
    # character.
    if authority is not None and path and not path.startswith('/'):
        raise ValueError('Cannot use path %r with authority' % path)
    if authority is None and path.startswith('//'):
        raise ValueError('Cannot use path %r without authority' % path)
    if not scheme and ':' in path.split('/', 1)[0]:
        raise ValueError('Cannot use path %r without scheme' % path)
    result += path

    if query is not None:
        if '#' in query:
            raise ValueError('Reserved character in %r' % query)
        result += '?' + query

    if fragment is not None:
        result += '#' + fragment

    return result


def urijoin(base, ref, strict=False):
    """Convert a URI reference relative to a base URI to its target
    URI string."""
    return uriunsplit(urisplit(base).transform(ref, strict))


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
