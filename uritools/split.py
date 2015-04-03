from __future__ import unicode_literals

import collections
import ipaddress
import re
import warnings

from .encoding import uridecode

_URI_COMPONENTS = ('scheme', 'authority', 'path', 'query', 'fragment')


def _ip_literal(address):
    # RFC 3986 3.2.2: In anticipation of future, as-yet-undefined IP
    # literal address formats, an implementation may use an optional
    # version flag to indicate such a format explicitly rather than
    # rely on heuristic determination.
    #
    #  IP-literal = "[" ( IPv6address / IPvFuture  ) "]"
    #
    #  IPvFuture  = "v" 1*HEXDIG "." 1*( unreserved / sub-delims / ":" )
    #
    # If a URI containing an IP-literal that starts with "v"
    # (case-insensitive), indicating that the version flag is present,
    # is dereferenced by an application that does not know the meaning
    # of that version flag, then the application should return an
    # appropriate error for "address mechanism not supported".
    if isinstance(address, bytes):
        address = address.decode('ascii')
    if address.startswith('v'):
        raise ValueError('address mechanism not supported')
    return ipaddress.IPv6Address(address)


def _ipv4_address(address):
    try:
        if isinstance(address, bytes):
            return ipaddress.IPv4Address(address.decode('ascii'))
        else:
            return ipaddress.IPv4Address(address)
    except ValueError:
        return None


class SplitResult(collections.namedtuple('SplitResult', _URI_COMPONENTS)):
    """Base class to hold :func:`urisplit` results."""

    __slots__ = ()  # prevent creation of instance dictionary

    @property
    def userinfo(self):
        authority = self.authority
        if authority is None:
            return None
        userinfo, present, _ = authority.rpartition(self.AT)
        if present:
            return userinfo
        else:
            return None

    @property
    def host(self):
        authority = self.authority
        if authority is None:
            return None
        _, _, hostinfo = authority.rpartition(self.AT)
        host, _, port = hostinfo.rpartition(self.COLON)
        if port.lstrip(self.DIGITS):
            return hostinfo
        else:
            return host

    @property
    def port(self):
        authority = self.authority
        if authority is None:
            return None
        _, present, port = authority.rpartition(self.COLON)
        if present and not port.lstrip(self.DIGITS):
            return port
        else:
            return None

    def geturi(self):
        """Return the re-combined version of the original URI as a string."""
        scheme, authority, path, query, fragment = self

        # RFC 3986 5.3. Component Recomposition
        result = []
        if scheme is not None:
            result.extend([scheme, self.COLON])
        if authority is not None:
            result.extend([self.SLASH, self.SLASH, authority])
        result.append(path)
        if query is not None:
            result.extend([self.QUEST, query])
        if fragment is not None:
            result.extend([self.HASH, fragment])
        return type(path)().join(result)

    def getscheme(self, default=None):
        """Return the URI scheme in canonical (lowercase) form, or `default`
        if the original URI did not contain a scheme component.

        """
        scheme = self.scheme
        if scheme is None:
            return default
        elif isinstance(scheme, bytes):
            return scheme.decode('ascii').lower()
        else:
            return scheme.lower()

    def getauthority(self, default=None, encoding='utf-8',
                     errors='strict'):  # pragma: no cover
        warnings.warn("getauthority() is deprecated", DeprecationWarning)
        authority = self.authority
        if authority is None:
            return default
        else:
            return uridecode(authority, encoding, errors)

    def getuserinfo(self, default=None, encoding='utf-8', errors='strict'):
        """Return the decoded userinfo subcomponent of the URI authority, or
        `default` if the original URI did not contain a userinfo
        field.

        """
        userinfo = self.userinfo
        if userinfo is None:
            return default
        else:
            return uridecode(userinfo, encoding, errors)

    def gethost(self, default=None, **kwargs):
        """Return the decoded host subcomponent of the URI authority, or
       `default` if the original URI did not contain a host.

        """
        if kwargs:  # pragma: no cover
            warnings.warn(
                "gethost() arguments encoding and errors are deprecated",
                DeprecationWarning
            )
        hostip = self.gethostip()
        if hasattr(hostip, 'compressed'):
            return hostip.compressed
        else:
            return hostip

    def gethostip(self, default=None, **kwargs):
        """Return the decoded host subcomponent of the URI authority as a
        string or an :mod:`ipaddress` address object, or `default` if
        the original URI did not contain a host.

        """
        if kwargs:  # pragma: no cover
            warnings.warn(
                "gethostip() arguments encoding and errors are deprecated",
                DeprecationWarning
            )
        host = self.host
        if host is None or (not host and default is not None):
            return default
        elif host.startswith(self.LBRACKET) and host.endswith(self.RBRACKET):
            return _ip_literal(host[1:-1])
        elif host.startswith(self.LBRACKET) or host.endswith(self.RBRACKET):
            raise ValueError('Invalid host %r' % host)  # FIXME: remove?
        else:
            return _ipv4_address(host) or uridecode(host, 'utf-8').lower()

    def getport(self, default=None):
        """Return the port subcomponent of the URI authority as an
        :class:`int`, or `default` if the original URI did not contain
        a port or if the port was empty.

        """
        port = self.port
        if port:
            return int(port)
        else:
            return default

    def getaddrinfo(self, port=None, family=0, type=0, proto=0,
                    flags=0):  # pragma: no cover
        import socket
        warnings.warn("getaddrinfo() is deprecated", DeprecationWarning)
        host = self.gethost()
        port = self.getport(port)
        if port is None and self.scheme:
            try:
                port = socket.getservbyname(self.getscheme())
            except socket.error:
                pass
        return socket.getaddrinfo(host, port, family, type, proto, flags)

    def getpath(self, encoding='utf-8', errors='strict'):
        """Return the decoded URI path."""
        return uridecode(self.path, encoding, errors)

    def getquery(self, default=None, encoding='utf-8', errors='strict'):
        """Return the decoded query string, or `default` if the original URI
        did not contain a query component.

        """
        query = self.query
        if query is None:
            return default
        else:
            return uridecode(query, encoding, errors)

    def getquerydict(self, delims=b';&', encoding='utf-8', errors='strict'):
        """Split the query string into individual components using the
        delimiter characters in `delims`, and return a dictionary of
        query parameters.

        """
        dict = collections.defaultdict(list)
        for name, value in self.getquerylist(delims, encoding, errors):
            dict[name].append(value)
        return dict

    def getquerylist(self, delims=b';&', encoding='utf-8', errors='strict'):
        """Split the query string into individual components using the
        delimiter characters in `delims` and return a list of `(name,
        value)` pairs, with names and values seperated by
        :const:`'='`.

        """
        if self.query:
            qsl = [self.query]
        else:
            return []
        if isinstance(self.query, bytes):
            delims = [delims[i:i+1] for i in range(len(delims))]
        else:
            delims = delims.decode()
        for delim in delims:
            qsl = [s for qs in qsl for s in qs.split(delim) if s]
        items = []
        for qs in qsl:
            parts = qs.partition(self.EQ)
            name = uridecode(parts[0], encoding, errors)
            value = uridecode(parts[2], encoding, errors) if parts[1] else None
            items.append((name, value))
        return items

    def getfragment(self, default=None, encoding='utf-8', errors='strict'):
        """Return the decoded fragment identifier, or `default` if the
        original URI did not contain a fragment component.

        """
        fragment = self.fragment
        if fragment is None:
            return default
        else:
            return uridecode(fragment, encoding, errors)

    def transform(self, ref, strict=False):
        """Convert a URI reference relative to `self` into a
        :class:`SplitResult` representing its target.

        """
        scheme, authority, path, query, fragment = self.RE.match(ref).groups()

        # RFC 3986 5.2.2. Transform References
        if scheme is not None and (strict or scheme != self.scheme):
            path = self.__normpath(path)
        elif authority is not None:
            scheme = self.scheme
            path = self.__normpath(path)
        elif not path:
            scheme = self.scheme
            authority = self.authority
            path = self.path
            query = self.query if query is None else query
        elif path.startswith(self.SLASH):
            scheme = self.scheme
            authority = self.authority
            path = self.__normpath(path)
        elif self.authority is not None and not self.path:
            scheme = self.scheme
            authority = self.authority
            path = self.__normpath(self.SLASH + path)
        else:
            scheme = self.scheme
            authority = self.authority
            pseg = self.path.rpartition(self.SLASH)[0]
            path = self.__normpath(self.SLASH.join((pseg, path)))
        return type(self)(scheme, authority, path, query, fragment)

    def __normpath(self, path):
        # RFC 3986 5.2.4. Remove Dot Segments
        out = []
        for s in path.split(self.SLASH):
            if s == self.DOT:
                continue
            elif s != self.DOT * 2:
                out.append(s)
            elif out:
                out.pop()
        # FIXME: verify (and refactor) this
        if path.startswith(self.SLASH) and (not out or out[0]):
            out.insert(0, type(path)())
        if path.endswith((self.SLASH + self.DOT, self.SLASH + self.DOT * 2)):
            out.append(type(path)())
        return self.SLASH.join(out)


class SplitResultBytes(SplitResult):

    __slots__ = ()  # prevent creation of instance dictionary

    # RFC 3986 Appendix B
    RE = re.compile(br"""
    (?:([^:/?#]+):)?        # scheme
    (?://([^/?#]*))?        # authority
    ([^?#]*)                # path
    (?:\?([^#]*))?          # query
    (?:\#(.*))?             # fragment
    """, flags=re.VERBOSE)

    # RFC 3986 2.2 gen-delims
    COLON, SLASH, QUEST, HASH, LBRACKET, RBRACKET, AT = (
        b':', b'/', b'?', b'#', b'[', b']', b'@'
    )

    DOT, EQ = b'.', b'='

    DIGITS = b'0123456789'


class SplitResultString(SplitResult):

    __slots__ = ()  # prevent creation of instance dictionary

    # RFC 3986 Appendix B
    RE = re.compile(r"""
    (?:([^:/?#]+):)?        # scheme
    (?://([^/?#]*))?        # authority
    ([^?#]*)                # path
    (?:\?([^#]*))?          # query
    (?:\#(.*))?             # fragment
    """, flags=re.VERBOSE)

    # RFC 3986 2.2 gen-delims
    COLON, SLASH, QUEST, HASH, LBRACKET, RBRACKET, AT = ':/?#[]@'

    DOT, EQ = '.='

    DIGITS = '0123456789'


def urisplit(uristring):
    """Split a well-formed URI string into a tuple with five components
    corresponding to a URI's general structure::

      <scheme>://<authority>/<path>?<query>#<fragment>

    """
    if isinstance(uristring, bytes):
        result = SplitResultBytes
    else:
        result = SplitResultString
    return result(*result.RE.match(uristring).groups())


def uriunsplit(parts):
    """Combine the elements of a five-item iterable into a URI string."""
    scheme, authority, path, query, fragment = parts
    if isinstance(path, bytes):
        result = SplitResultBytes
    else:
        result = SplitResultString
    return result(scheme, authority, path, query, fragment).geturi()
