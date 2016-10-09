import collections
import ipaddress
import re

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
    if address.startswith(u'v'):
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
        return self.EMPTY.join(result)

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

    def gethost(self, default=None):
        """Return the decoded host subcomponent of the URI authority as a
        string or an :mod:`ipaddress` address object, or `default` if
        the original URI did not contain a host.

        """
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

    def getpath(self, encoding='utf-8', errors='strict'):
        """Return the normalized decoded URI path."""
        path = self.__remove_dot_segments(self.path)
        return uridecode(path, encoding, errors)

    def getquery(self, default=None, encoding='utf-8', errors='strict'):
        """Return the decoded query string, or `default` if the original URI
        did not contain a query component.

        """
        query = self.query
        if query is None:
            return default
        else:
            return uridecode(query, encoding, errors)

    def getquerydict(self, sep='&', encoding='utf-8', errors='strict'):
        """Split the query component into individual `name=value` pairs
        separated by `sep` and return a dictionary of query variables.
        The dictionary keys are the unique query variable names and
        the values are lists of values for each name.

        """
        dict = collections.defaultdict(list)
        for name, value in self.getquerylist(sep, encoding, errors):
            dict[name].append(value)
        return dict

    def getquerylist(self, sep='&', encoding='utf-8', errors='strict'):
        """Split the query component into individual `name=value` pairs
        separated by `sep`, and return a list of `(name, value)`
        tuples.

        """
        if not self.query:
            return []
        elif isinstance(sep, type(self.query)):
            qsl = self.query.split(sep)
        elif isinstance(sep, bytes):
            qsl = self.query.split(sep.decode('ascii'))
        else:
            qsl = self.query.split(sep.encode('ascii'))
        items = []
        for parts in [qs.partition(self.EQ) for qs in qsl if qs]:
            name = uridecode(parts[0], encoding, errors)
            if parts[1]:
                value = uridecode(parts[2], encoding, errors)
            else:
                value = None
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
        """Transform a URI reference relative to `self` into a
        :class:`SplitResult` representing its target URI.

        """
        scheme, authority, path, query, fragment = self.RE.match(ref).groups()

        # RFC 3986 5.2.2. Transform References
        if scheme is not None and (strict or scheme != self.scheme):
            path = self.__remove_dot_segments(path)
        elif authority is not None:
            scheme = self.scheme
            path = self.__remove_dot_segments(path)
        elif not path:
            scheme = self.scheme
            authority = self.authority
            path = self.path
            query = self.query if query is None else query
        elif path.startswith(self.SLASH):
            scheme = self.scheme
            authority = self.authority
            path = self.__remove_dot_segments(path)
        else:
            scheme = self.scheme
            authority = self.authority
            path = self.__remove_dot_segments(self.__merge(path))
        return type(self)(scheme, authority, path, query, fragment)

    def __merge(self, path):
        # RFC 3986 5.2.3. Merge Paths
        if self.authority is not None and not self.path:
            return self.SLASH + path
        else:
            parts = self.path.rpartition(self.SLASH)
            return parts[1].join((parts[0], path))

    @classmethod
    def __remove_dot_segments(cls, path):
        # RFC 3986 5.2.4. Remove Dot Segments
        pseg = []
        for s in path.split(cls.SLASH):
            if s == cls.DOT:
                continue
            elif s != cls.DOTDOT:
                pseg.append(s)
            elif len(pseg) == 1 and not pseg[0]:
                continue
            elif pseg and pseg[-1] != cls.DOTDOT:
                pseg.pop()
            else:
                pseg.append(s)
        # adjust for trailing '/.' or '/..'
        if path.rpartition(cls.SLASH)[2] in (cls.DOT, cls.DOTDOT):
            pseg.append(cls.EMPTY)
        if path and len(pseg) == 1 and pseg[0] == cls.EMPTY:
            pseg.insert(0, cls.DOT)
        return cls.SLASH.join(pseg)


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

    # RFC 3986 3.3 dot-segments
    DOT, DOTDOT = b'.', b'..'

    EMPTY, EQ = b'', b'='

    DIGITS = b'0123456789'


class SplitResultUnicode(SplitResult):

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
    COLON, SLASH, QUEST, HASH, LBRACKET, RBRACKET, AT = (
        u':', u'/', u'?', u'#', u'[', u']', u'@'
    )

    # RFC 3986 3.3 dot-segments
    DOT, DOTDOT = u'.', u'..'

    EMPTY, EQ = u'', u'='

    DIGITS = u'0123456789'


def urisplit(uristring):
    """Split a well-formed URI string into a tuple with five components
    corresponding to a URI's general structure::

      <scheme>://<authority>/<path>?<query>#<fragment>

    """
    if isinstance(uristring, bytes):
        result = SplitResultBytes
    else:
        result = SplitResultUnicode
    return result(*result.RE.match(uristring).groups())


def uriunsplit(parts):
    """Combine the elements of a five-item iterable into a URI string."""
    scheme, authority, path, query, fragment = parts
    if isinstance(path, bytes):
        result = SplitResultBytes
    else:
        result = SplitResultUnicode
    return result(scheme, authority, path, query, fragment).geturi()
