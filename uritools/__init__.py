"""RFC 3986 compliant, scheme-agnostic replacement for urlparse.

The urlparse module is not compliant with RFC 3986, and is generally
unusable with custom (private) URI schemes.  This module provides
compliant replacements for urlsplit and urlunsplit, as well as a
convenient way to compose URIs.

"""
import collections
import re

__version__ = '0.0.2'


# RFC 3986: 2.2. Reserved Characters
GEN_DELIMS = ':/?#[]@'

SUB_DELIMS = "!$&'()*+,;="

RESERVED_CHARS = GEN_DELIMS + SUB_DELIMS

# RFC 3986: 2.3. Unreserved Characters
UNRESERVED_CHARS = ('ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                    'abcdefghijklmnopqrstuvwxyz'
                    '0123456789'
                    '_.-~')

# RFC 3986: 3. Syntax Components
URI_COMPONENTS = ('scheme', 'authority', 'path', 'query', 'fragment')

# RFC 3986: Appendix B
URI_RE = re.compile(r"""
(?:([^:/?#]+):)?  # scheme
(?://([^/?#]*))?  # authority
([^?#]*)          # path
(?:\?([^#]*))?    # query
(?:\#(.*))?       # fragment
""", flags=(re.VERBOSE))


def encode(s, reserved='', encoding='utf-8'):
    from urllib import quote
    # FIXME: more efficient implementation (w/o urllib?)
    safe = set(RESERVED_CHARS + UNRESERVED_CHARS) - set(reserved)
    return quote(s.encode(encoding), str(safe))


def decode(s, encoding='utf-8'):
    from urllib import unquote
    return unquote(s).decode(encoding)


class SplitResult(collections.namedtuple('SplitResult', URI_COMPONENTS)):

    def getscheme(self, encoding='utf-8'):
        return decode(self.scheme, encoding=encoding)

    def getauthority(self, encoding='utf-8'):
        return decode(self.authority, encoding=encoding)

    def getpath(self, encoding='utf-8'):
        return decode(self.path, encoding=encoding)

    def getquery(self, encoding='utf-8'):
        return decode(self.query, encoding=encoding)

    def getfragment(self, encoding='utf-8'):
        return decode(self.fragment, encoding=encoding)

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
    uri = ''
    if scheme:
        if any(c in ':/?#' for c in scheme):
            raise ValueError('Reserved character in "%s"' % scheme)
        uri += scheme + ':'
    if authority:
        if any(c in '/?#' for c in authority):
            raise ValueError('Reserved character in "%s"' % authority)
        uri += '//' + authority
    if path:
        if any(c in '?#' for c in path):
            raise ValueError('Reserved character in "%s"' % path)
        # RFC 3986 3.3: If a URI contains an authority component, then
        # the path component must either be empty or begin with a
        # slash ("/") character.  If a URI does not contain an
        # authority component, then the path cannot begin with two
        # slash characters ("//")
        if authority and not path.startswith('/'):
            raise ValueError('Cannot use path "%s" with authority' % path)
        if not authority and path.startswith('//'):
            raise ValueError('Cannot use path "%s" without authority' % path)
        uri += path
    if query:
        if '#' in query:
            raise ValueError('Reserved character in "%s"' % query)
        uri += '?' + query
    if fragment:
        uri += '#' + fragment
    return uri


def uricompose(scheme=None, authority=None, path='', query=None,
               fragment=None, encoding='utf-8'):
    if scheme:
        scheme = encode(scheme, reserved=':/?#', encoding=encoding)
    if authority:
        authority = encode(authority, reserved='/?#', encoding=encoding)
    if path:
        path = encode(path, reserved='?#', encoding=encoding)
    if query:
        query = encode(query, reserved='#', encoding=encoding)
    if fragment:
        fragment = encode(fragment, encoding=encoding)
    return uriunsplit((scheme, authority, path, query, fragment))
