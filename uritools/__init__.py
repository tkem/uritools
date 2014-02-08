"""RFC 3986 compliant, scheme-agnostic replacement for urlparse.

The urlparse module is not compliant with RFC 3986, and is generally
unusable with custom (private) URI schemes.  This module provides
compliant replacements for urlsplit and urlunsplit, as well as a
convenient way to compose URIs.

"""
import collections
import re

from urllib import quote, unquote

__version__ = '0.0.2'

# see RFC 3986 Appendix B.
URI_RE = re.compile(r"""
(?:([^:/?#]+):)?  # scheme
(?://([^/?#]*))?  # authority
([^?#]*)          # path
(?:\?([^#]*))?    # query
(?:\#(.*))?       # fragment
""", flags=(re.VERBOSE))

URI_FIELDS = ('scheme', 'authority', 'path', 'query', 'fragment')

GEN_DELIMS = ':/?#[]@'

SUB_DELIMS = "!$&'()*+,;="

RESERVED = GEN_DELIMS + SUB_DELIMS


class SplitResult(collections.namedtuple('SplitResult', URI_FIELDS)):

    def getscheme(self):
        return unquote(self.scheme)

    def getauthority(self):
        return unquote(self.authority)

    def getpath(self):
        return unquote(self.path)

    def getquery(self):
        return unquote(self.query)

    def getfragment(self):
        return unquote(self.fragment)

    def geturi(self):
        return uriunsplit(self)


def urisplit(uri):
    """Split a URI into a named tuple with five components:
    <scheme>://<authority>/<path>?<query>#<fragment>.  Note that
    %-escapes are not expaneded.

    """
    return SplitResult(*URI_RE.match(uri).groups())


def uriunsplit(data):
    """Combine the elements of a tuple as returned by urisplit() into a
    complete URI as a string.  The data argument can be any five-item
    iterable.  Note that this may result in a slightly different, but
    equivalent URI string.

    """
    scheme, authority, path, query, fragment = data
    if authority:
        if path.startswith('/'):
            uri = '//' + authority + path
        else:
            uri = '//' + authority + '/' + path
    elif path.startswith('//'):
        # RFC 3986 3.3: If a URI does not contain an authority
        # component, then the path cannot begin with two slash
        # characters ("//").
        raise ValueError('invalid uri path: %s' % path)
    else:
        uri = path
    if scheme:
        uri = scheme + ':' + uri
    if query:
        uri += '?' + query
    if fragment:
        uri += '#' + fragment
    return uri


def uricompose(scheme=None, authority=None, path='', query=None, fragment=None):
    if scheme:
        scheme = quote(scheme, SUB_DELIMS)
    if authority:
        authority = quote(authority, SUB_DELIMS + ':')
    if path:
        path = quote(path, SUB_DELIMS + ':/')
    if query:
        query = quote(query, SUB_DELIMS + ':/?')
    if fragment:
        fragment = quote(fragment, SUB_DELIMS + ':/?#')
    return uriunsplit((scheme, authority, path, query, fragment))
