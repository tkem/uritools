from __future__ import unicode_literals

import collections
import ipaddress
import re

from .encoding import uridecode

URI_COMPONENTS = ('scheme', 'authority', 'path', 'query', 'fragment')


def parse_ip_literal(address, as_string=False):
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
    if address.startswith('v'):
        raise ipaddress.AddressValueError('address mechanism not supported')
    elif as_string:
        # TBD: compact form or original?
        ipaddress.IPv6Address(address)
        return address.lower()
    else:
        return ipaddress.IPv6Address(address)


class SplitResult(collections.namedtuple('SplitResult', URI_COMPONENTS)):
    """Base class to hold :func:`urisplit` results.

    Do not try to create instances of this class directly.  Use the
    :func:`urisplit` factory function instead.

    """

    __slots__ = ()  # prevent creation of instance dictionary

    @property
    def userinfo(self):
        raise NotImplementedError

    @property
    def host(self):
        raise NotImplementedError

    @property
    def port(self):
        raise NotImplementedError

    def geturi(self):
        """Return the re-combined version of the original URI as a string."""
        raise NotImplementedError

    def getscheme(self, default=None):
        """Return the URI scheme in canonical (lowercase) form, or `default`
        if the original URI did not contain a scheme component.

        """
        raise NotImplementedError

    def getauthority(self, default=None, encoding='utf-8', errors='strict'):
        """Return the decoded URI authority, or `default` if the original URI
        did not contain an authority component.

        """
        authority = self.authority
        if authority is not None:
            return uridecode(authority, encoding, errors)
        else:
            return default

    def getpath(self, encoding='utf-8', errors='strict'):
        """Return the decoded URI path."""
        return uridecode(self.path, encoding, errors)

    def getquery(self, default=None, encoding='utf-8', errors='strict'):
        """Return the decoded query string, or `default` if the original URI
        did not contain a query component.

        """
        query = self.query
        if query is not None:
            return uridecode(query, encoding, errors)
        else:
            return default

    def getfragment(self, default=None, encoding='utf-8', errors='strict'):
        """Return the decoded fragment identifier, or `default` if the
        original URI did not contain a fragment component.

        """
        fragment = self.fragment
        if fragment is not None:
            return uridecode(fragment, encoding, errors)
        else:
            return default

    def getuserinfo(self, default=None, encoding='utf-8', errors='strict'):
        """Return the decoded userinfo subcomponent of the URI authority, or
        `default` if the original URI did not contain a userinfo
        field.

        """
        userinfo = self.userinfo
        if userinfo is not None:
            return uridecode(userinfo, encoding, errors)
        else:
            return default

    def gethost(self, default=None, encoding='utf-8', errors='strict'):
        """Return the decoded host subcomponent of the URI authority, or
        `default` if the original URI did not contain a host.

        If the host represents an internationalized domain name
        intended for resolution via DNS, the :const:`'idna'` encoding
        must be specified to return a Unicode domain name.

        """
        raise NotImplementedError

    def gethostip(self, default=None, encoding='utf-8', errors='strict'):
        """Return the decoded host subcomponent of the URI authority as a
        string or an :mod:`ipaddress` address object, or `default` if
        the original URI did not contain a host.

        """
        raise NotImplementedError

    def getport(self, default=None):
        """Return the port subcomponent of the URI authority as an
        :class:`int`, or `default` if the original URI did not contain
        a port, or if the port was empty.

        """
        return int(self.port) if self.port else default

    def getaddrinfo(self, port=None, family=0, type=0, proto=0, flags=0):
        """Translate the host and port subcomponents of the URI
        authority into a sequence of 5-tuples as reported by
        :func:`socket.getaddrinfo`.

        If the URI authority does not contain a port subcomponent, or
        the port subcomponent is empty, the optional `port` argument
        is used.  If no `port` argument is given, the URI scheme is
        interpreted as a service name, and the port number for that
        service is used.  If no matching service is found,
        :const:`None` is passed to :func:`socket.getaddrinfo` for the
        port value.

        The optional `family`, `type`, `proto` and `flags` arguments
        are passed to :func:`socket.getaddrinfo` unchanged.

        """
        import socket
        host = self.gethost()
        port = self.getport(port)
        if port is None and self.scheme:
            try:
                port = socket.getservbyname(self.getscheme())
            except socket.error:
                pass
        return socket.getaddrinfo(host, port, family, type, proto, flags)

    def getquerydict(self, delims=b';&', encoding='utf-8', errors='strict'):
        """Split the query string into individual components using the
        delimiter characters in `delims`, and return a dictionary of
        query parameters.

        The dictionary keys are the unique decoded query parameter
        names, and the values are lists of decoded values for each
        name, with names and values seperated by :const:`'='`.

        """
        dict = collections.defaultdict(list)
        for name, value in self.getquerylist(delims, encoding, errors):
            dict[name].append(value)
        return dict

    def getquerylist(self, delims=b';&', encoding='utf-8', errors='strict'):
        """Split the query string into individual components using the
        delimiter characters in `delims`, and return a list of `(name,
        value)` pairs, where names and values are seperated by
        :const:`'='`.

        """
        raise NotImplementedError

    def transform(self, ref, strict=False):
        """Convert a URI reference relative to `self` into a
        :class:`SplitResult` representing its target.

        If `strict` is :const:`False`, a scheme in the reference is
        ignored if it is identical to :attr:`self.scheme`.

        """
        raise NotImplementedError


class SplitResultBytes(SplitResult):

    __slots__ = ()  # prevent creation of instance dictionary

    # RFC 3986 Appendix B
    re = re.compile(br"""
    (?:([^:/?#]+):)?        # scheme
    (?://([^/?#]*))?        # authority
    ([^?#]*)                # path
    (?:\?([^#]*))?          # query
    (?:\#(.*))?             # fragment
    """, flags=re.VERBOSE)

    @property
    def userinfo(self):
        parts = (self.authority or b'').partition(b'@')
        return parts[0] if parts[1] else None

    @property
    def host(self):
        authority = self.authority
        if not authority:
            return authority
        parts = authority.partition(b'@')
        netloc = parts[2] if parts[1] else parts[0]
        host, _, port = netloc.rpartition(b':')
        return host if not port.lstrip(b'0123456789') else netloc

    @property
    def port(self):
        parts = (self.authority or b'').rpartition(b':')
        if parts[1] and not parts[2].lstrip(b'0123456789'):
            return parts[2]
        else:
            return None

    def geturi(self):
        scheme, authority, path, query, fragment = self
        # RFC 3986 5.3. Component Recomposition
        result = b''
        if scheme is not None:
            result += scheme + b':'
        if authority is not None:
            result += b'//' + authority
        result += path
        if query is not None:
            result += b'?' + query
        if fragment is not None:
            result += b'#' + fragment
        return result

    def getscheme(self, default=None):
        if self.scheme is not None:
            return self.scheme.decode().lower()
        else:
            return default

    def gethost(self, default=None, encoding='utf-8', errors='strict'):
        host = self.host
        if host is None or (not host and default is not None):
            return default
        elif host.startswith(b'[') and host.endswith(b']'):
            return parse_ip_literal(host[1:-1].decode(encoding), True)
        elif host.startswith(b'[') or host.endswith(b']'):
            raise ValueError('Invalid host %r' % host)
        else:
            return uridecode(host, encoding, errors).lower()

    def gethostip(self, default=None, encoding='utf-8', errors='strict'):
        host = self.host
        if host is None or (not host and default is not None):
            return default
        elif host.startswith(b'[') and host.endswith(b']'):
            return parse_ip_literal(host[1:-1].decode(encoding))
        elif host.startswith(b'[') or host.endswith(b']'):
            raise ValueError('Invalid host %r' % host)
        else:
            try:
                return ipaddress.IPv4Address(host.decode(encoding))
            except ValueError:
                return uridecode(host, encoding, errors).lower()

    def getquerylist(self, delims=b';&', encoding='utf-8', errors='strict'):
        qsl = [self.query] if self.query else []
        for delim in (delims[i:i+1] for i in range(len(delims))):
            qsl = [s for qs in qsl for s in qs.split(delim) if s]
        items = []
        for qs in qsl:
            parts = qs.partition(b'=')
            name = uridecode(parts[0], encoding, errors)
            value = uridecode(parts[2], encoding, errors) if parts[1] else None
            items.append((name, value))
        return items

    def transform(self, ref, strict=False):
        scheme, authority, path, query, fragment = self.re.match(ref).groups()
        result = SplitResultBytes
        # RFC 3986 5.2.2. Transform References
        if scheme is not None and (strict or scheme != self.scheme):
            path = self.normpath(path)
            return result(scheme, authority, path, query, fragment)
        elif authority is not None:
            path = self.normpath(path)
            return result(self.scheme, authority, path, query, fragment)
        elif not path:
            path = self.path
            if query is None:
                query = self.query
        elif path.startswith(b'/'):
            path = self.normpath(path)
        elif self.authority is not None and not self.path:
            path = self.normpath(b'/' + path)
        else:
            path = self.normpath(self.path[:self.path.rfind(b'/') + 1] + path)
        return result(self.scheme, self.authority, path, query, fragment)

    @staticmethod
    def normpath(path):
        # RFC 3986 5.2.4. Remove Dot Segments
        out = []
        for s in path.split(b'/'):
            if s == b'.':
                continue
            elif s != b'..':
                out.append(s)
            elif out:
                out.pop()
        if path.startswith(b'/') and (not out or out[0]):
            out.insert(0, b'')
        if path.endswith((b'/.', b'/..')):
            out.append(b'')
        return b'/'.join(out)


class SplitResultString(SplitResult):

    __slots__ = ()  # prevent creation of instance dictionary

    # RFC 3986 Appendix B
    re = re.compile(r"""
    (?:([^:/?#]+):)?        # scheme
    (?://([^/?#]*))?        # authority
    ([^?#]*)                # path
    (?:\?([^#]*))?          # query
    (?:\#(.*))?             # fragment
    """, flags=re.VERBOSE)

    @property
    def userinfo(self):
        parts = (self.authority or '').partition('@')
        return parts[0] if parts[1] else None

    @property
    def host(self):
        authority = self.authority
        if not authority:
            return authority
        parts = authority.partition('@')
        netloc = parts[2] if parts[1] else parts[0]
        host, _, port = netloc.rpartition(':')
        return host if not port.lstrip('0123456789') else netloc

    @property
    def port(self):
        parts = (self.authority or '').rpartition(':')
        if parts[1] and not parts[2].lstrip('0123456789'):
            return parts[2]
        else:
            return None

    def geturi(self):
        scheme, authority, path, query, fragment = self
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

    def getscheme(self, default=None):
        if self.scheme is not None:
            return self.scheme.lower()
        else:
            return default

    def gethost(self, default=None, encoding='utf-8', errors='strict'):
        host = self.host
        if host is None or (not host and default is not None):
            return default
        elif host.startswith('[') and host.endswith(']'):
            return parse_ip_literal(host[1:-1], True)
        elif host.startswith('[') or host.endswith(']'):
            raise ValueError('Invalid host %r' % host)
        else:
            return uridecode(host, encoding, errors).lower()

    def gethostip(self, default=None, encoding='utf-8', errors='strict'):
        host = self.host
        if host is None or (not host and default is not None):
            return default
        elif host.startswith('[') and host.endswith(']'):
            return parse_ip_literal(host[1:-1])
        elif host.startswith('[') or host.endswith(']'):
            raise ValueError('Invalid host %r' % host)
        else:
            try:
                return ipaddress.IPv4Address(host)
            except ValueError:
                return uridecode(host, encoding, errors).lower()

    def getquerylist(self, delims=b';&', encoding='utf-8', errors='strict'):
        qsl = [self.query] if self.query else []
        for delim in delims.decode():
            qsl = [s for qs in qsl for s in qs.split(delim) if s]
        items = []
        for qs in qsl:
            parts = qs.partition('=')
            name = uridecode(parts[0], encoding, errors)
            value = uridecode(parts[2], encoding, errors) if parts[1] else None
            items.append((name, value))
        return items

    def transform(self, ref, strict=False):
        scheme, authority, path, query, fragment = self.re.match(ref).groups()
        result = SplitResultString
        # RFC 3986 5.2.2. Transform References
        if scheme is not None and (strict or scheme != self.scheme):
            path = self.normpath(path)
            return result(scheme, authority, path, query, fragment)
        elif authority is not None:
            path = self.normpath(path)
            return result(self.scheme, authority, path, query, fragment)
        elif not path:
            path = self.path
            if query is None:
                query = self.query
        elif path.startswith('/'):
            path = self.normpath(path)
        elif self.authority is not None and not self.path:
            path = self.normpath('/' + path)
        else:
            path = self.normpath(self.path[:self.path.rfind('/') + 1] + path)
        return result(self.scheme, self.authority, path, query, fragment)

    @staticmethod
    def normpath(path):
        # RFC 3986 5.2.4. Remove Dot Segments
        out = []
        for s in path.split('/'):
            if s == '.':
                continue
            elif s != '..':
                out.append(s)
            elif out:
                out.pop()
        if path.startswith('/') and (not out or out[0]):
            out.insert(0, '')
        if path.endswith(('/.', '/..')):
            out.append('')
        return '/'.join(out)


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
    | :attr:`port`      |       | Port subcomponent of authority as a         |
    |                   |       | (possibly empty) string,                    |
    |                   |       | or :const:`None` if not present             |
    +-------------------+-------+---------------------------------------------+

    """
    if isinstance(string, type('')):
        result = SplitResultString
    else:
        result = SplitResultBytes
    return result(*result.re.match(string).groups())


def uriunsplit(parts):
    """Combine the elements of a five-item iterable into a URI string.

    """
    scheme, authority, path, query, fragment = parts
    if isinstance(path, type('')):
        result = SplitResultString
    else:
        result = SplitResultBytes
    return result(scheme, authority, path, query, fragment).geturi()


def urijoin(base, ref, strict=False):
    """Convert a URI reference relative to a base URI to its target URI
    string.

    If `strict` is :const:`False`, a scheme in the reference is
    ignored if it is identical to the base URI's scheme.

    """
    if isinstance(base, type(ref)):
        return urisplit(base).transform(ref, strict).geturi()
    elif isinstance(base, type('')):
        return urisplit(base).transform(ref.decode(), strict).geturi()
    else:
        return urisplit(base.decode()).transform(ref, strict).geturi()
