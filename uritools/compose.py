import collections
import collections.abc
import ipaddress
import numbers
import re

from .chars import SUB_DELIMS
from .encoding import uriencode
from .split import uriunsplit

# RFC 3986 3.1: scheme = ALPHA *( ALPHA / DIGIT / "+" / "-" / "." )
_SCHEME_RE = re.compile(b"^[A-Za-z][A-Za-z0-9+.-]*$")

# RFC 3986 3.2: authority = [ userinfo "@" ] host [ ":" port ]
_AUTHORITY_RE_BYTES = re.compile(b"^(?:(.*)@)?(.*?)(?::([0-9]*))?$")
_AUTHORITY_RE_STR = re.compile("^(?:(.*)@)?(.*?)(?::([0-9]*))?$")

# safe component characters
_SAFE_USERINFO = SUB_DELIMS + ":"
_SAFE_HOST = SUB_DELIMS
_SAFE_PATH = SUB_DELIMS + ":@/"
_SAFE_QUERY = SUB_DELIMS + ":@/?"
_SAFE_FRAGMENT = SUB_DELIMS + ":@/?"


def _scheme(scheme):
    if _SCHEME_RE.match(scheme):
        return scheme.lower()
    else:
        raise ValueError("Invalid scheme component")


def _authority(userinfo, host, port, encoding):
    authority = []

    if userinfo is not None:
        authority.append(uriencode(userinfo, _SAFE_USERINFO, encoding))
        authority.append(b"@")

    if isinstance(host, ipaddress.IPv6Address):
        authority.append(b"[" + host.compressed.encode() + b"]")
    elif isinstance(host, ipaddress.IPv4Address):
        authority.append(host.compressed.encode())
    elif isinstance(host, bytes):
        authority.append(_host(host))
    elif host is not None:
        authority.append(_host(host.encode("utf-8")))

    if isinstance(port, numbers.Number):
        authority.append(_port(str(port).encode()))
    elif isinstance(port, bytes):
        authority.append(_port(port))
    elif port is not None:
        authority.append(_port(port.encode()))

    return b"".join(authority) if authority else None


def _ip_literal(address):
    if address.startswith("v"):
        raise ValueError("Address mechanism not supported")
    else:
        return b"[" + ipaddress.IPv6Address(address).compressed.encode() + b"]"


def _host(host):
    # RFC 3986 3.2.3: Although host is case-insensitive, producers and
    # normalizers should use lowercase for registered names and
    # hexadecimal addresses for the sake of uniformity, while only
    # using uppercase letters for percent-encodings.
    if host.startswith(b"[") and host.endswith(b"]"):
        return _ip_literal(host[1:-1].decode())
    # check for IPv6 addresses as returned by SplitResult.gethost()
    try:
        return _ip_literal(host.decode("utf-8"))
    except ValueError:
        return uriencode(host.lower(), _SAFE_HOST, "utf-8")


def _port(port):
    # RFC 3986 3.2.3: URI producers and normalizers should omit the
    # port component and its ":" delimiter if port is empty or if its
    # value would be the same as that of the scheme's default.
    if port.lstrip(b"0123456789"):
        raise ValueError("Invalid port subcomponent")
    elif port:
        return b":" + port
    else:
        return b""


def _querylist(items, sep, encoding):
    terms = []
    append = terms.append
    safe = _SAFE_QUERY.replace(sep, "")
    for key, value in items:
        name = uriencode(key, safe, encoding)
        if value is None:
            append(name)
        elif isinstance(value, (bytes, str)):
            append(name + b"=" + uriencode(value, safe, encoding))
        else:
            append(name + b"=" + uriencode(str(value), safe, encoding))
    return sep.encode("ascii").join(terms)


def _querydict(mapping, sep, encoding):
    items = []
    for key, value in mapping.items():
        if isinstance(value, (bytes, str)):
            items.append((key, value))
        elif isinstance(value, collections.abc.Iterable):
            items.extend([(key, v) for v in value])
        else:
            items.append((key, value))
    return _querylist(items, sep, encoding)


def uricompose(
    scheme=None,
    authority=None,
    path="",
    query=None,
    fragment=None,
    userinfo=None,
    host=None,
    port=None,
    querysep="&",
    encoding="utf-8",
):
    """Compose a URI reference string from its individual components."""

    # RFC 3986 3.1: Scheme names consist of a sequence of characters
    # beginning with a letter and followed by any combination of
    # letters, digits, plus ("+"), period ("."), or hyphen ("-").
    # Although schemes are case-insensitive, the canonical form is
    # lowercase and documents that specify schemes must do so with
    # lowercase letters.  An implementation should accept uppercase
    # letters as equivalent to lowercase in scheme names (e.g., allow
    # "HTTP" as well as "http") for the sake of robustness but should
    # only produce lowercase scheme names for consistency.
    if isinstance(scheme, bytes):
        scheme = _scheme(scheme)
    elif scheme is not None:
        scheme = _scheme(scheme.encode())

    # authority must be string type or three-item iterable
    if authority is None:
        authority = (None, None, None)
    elif isinstance(authority, bytes):
        authority = _AUTHORITY_RE_BYTES.match(authority).groups()
    elif isinstance(authority, str):
        authority = _AUTHORITY_RE_STR.match(authority).groups()
    elif not isinstance(authority, collections.abc.Iterable):
        raise TypeError("Invalid authority type")
    elif len(authority) != 3:
        raise ValueError("Invalid authority length")
    authority = _authority(
        userinfo if userinfo is not None else authority[0],
        host if host is not None else authority[1],
        port if port is not None else authority[2],
        encoding,
    )

    # RFC 3986 3.3: If a URI contains an authority component, then the
    # path component must either be empty or begin with a slash ("/")
    # character.  If a URI does not contain an authority component,
    # then the path cannot begin with two slash characters ("//").
    path = uriencode(path, _SAFE_PATH, encoding)
    if authority is not None and path and not path.startswith(b"/"):
        raise ValueError("Invalid path with authority component")
    if authority is None and path.startswith(b"//"):
        raise ValueError("Invalid path without authority component")

    # RFC 3986 4.2: A path segment that contains a colon character
    # (e.g., "this:that") cannot be used as the first segment of a
    # relative-path reference, as it would be mistaken for a scheme
    # name.  Such a segment must be preceded by a dot-segment (e.g.,
    # "./this:that") to make a relative-path reference.
    if scheme is None and authority is None and not path.startswith(b"/"):
        if b":" in path.partition(b"/")[0]:
            path = b"./" + path

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
    if isinstance(query, (bytes, str)):
        query = uriencode(query, _SAFE_QUERY, encoding)
    elif isinstance(query, collections.abc.Mapping):
        query = _querydict(query, querysep, encoding)
    elif isinstance(query, collections.abc.Iterable):
        query = _querylist(query, querysep, encoding)
    elif query is not None:
        raise TypeError("Invalid query type")

    # RFC 3986 3.5: The characters slash ("/") and question mark ("?")
    # are allowed to represent data within the fragment identifier.
    # Beware that some older, erroneous implementations may not handle
    # this data correctly when it is used as the base URI for relative
    # references.
    if fragment is not None:
        fragment = uriencode(fragment, _SAFE_FRAGMENT, encoding)

    # return URI reference as `str`
    return uriunsplit((scheme, authority, path, query, fragment)).decode()
