from .encoding import uridecode
from .normpath import urinormpath
from .regex import RE, _AUTHORITY_RE, _IPV6_ADDRESS_RE

import collections


_URI_COMPONENTS = ('scheme', 'authority', 'path', 'query', 'fragment')


def _splitauth(authority):
    if authority is None:
        return (None, None, None)
    try:
        return _AUTHORITY_RE.match(authority).groups()
    except TypeError:
        # Python 3: handle authority as bytes
        groups = _AUTHORITY_RE.match(authority.decode('ascii')).groups()
        return[None if g is None else g.encode('ascii') for g in groups]


class SplitResult(collections.namedtuple('SplitResult', _URI_COMPONENTS)):
    """Class to hold :func:`urisplit` results."""

    __splitauth = None

    @property
    def _splitauth(self):
        if self.__splitauth is None:
            self.__splitauth = _splitauth(self.authority)
        return self.__splitauth

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
        if the original URI did not contain a scheme component.

        """
        if self.scheme is None:
            return default
        elif isinstance(self.scheme, bytes):
            return self.scheme.decode('ascii').lower()
        else:
            return self.scheme.lower()

    def getauthority(self, default=None, encoding='utf-8'):
        """Return the decoded URI authority, or `default` if the original URI
        did not contain an authority component.

        """
        if self.authority is not None:
            return uridecode(self.authority, encoding)
        else:
            return default

    def getpath(self, encoding='utf-8'):
        """Return the decoded URI path."""
        return uridecode(self.path, encoding)

    def getquery(self, default=None, encoding='utf-8'):
        """Return the decoded query string, or `default` if the original URI
        did not contain a query component.

        """
        if self.query is not None:
            return uridecode(self.query, encoding)
        else:
            return default

    def getfragment(self, default=None, encoding='utf-8'):
        """Return the decoded fragment identifier, or `default` if the
        original URI did not contain a fragment component.

        """
        if self.fragment is not None:
            return uridecode(self.fragment, encoding)
        else:
            return default

    def getuserinfo(self, default=None, encoding='utf-8'):
        """Return the decoded userinfo subcomponent of the URI authority, or
        `default` if the original URI did not contain a userinfo
        field.

        """
        if self.userinfo is not None:
            return uridecode(self.userinfo, encoding)
        else:
            return default

    def gethost(self, default=None, encoding='utf-8'):
        """Return the decoded host subcomponent of the URI authority, or
        `default` if the original URI did not contain a host.

        If the host represents an internationalized domain name
        intended for resolution via DNS, the :const:`'idna'` encoding
        must be specified to return a Unicode domain name.

        """
        host = self.host
        if isinstance(host, bytes):
            host = host.decode(encoding)
        # RFC 3986 3.2.2: If the URI scheme defines a default for
        # host, then that default applies when the host subcomponent
        # is undefined or when the registered name is empty (zero
        # length).
        if host is None or (default is not None and not host):
            return default
        elif not host.startswith('[') or not host.endswith(']'):
            return uridecode(host, encoding)
        elif _IPV6_ADDRESS_RE.match(host[1:-1]):
            return host[1:-1]
        else:
            raise ValueError('Invalid IP literal: %s' % host)

    def getport(self, default=None):
        """Return the port subcomponent of the URI authority as an
        :class:`int`, or `default` if the original URI did not contain
        a port, or if the port was empty.

        """
        return int(self.port) if self.port else default

    def getaddrinfo(self, family=0, type=0, proto=0, flags=0):
        """Translate the host and port subcomponents of the URI authority into
        a sequence of 5-tuples as reported by
        :func:`socket.getaddrinfo`.

        If the URI authority does not contain a port subcomponent, the
        URI scheme is interpreted as a service name.  The optional
        `family`, `type`, `proto` and `flags` arguments are passed to
        :func:`socket.getaddrinfo` as-is,

        """
        import socket
        host = self.host
        port = self.port or self.scheme
        return socket.getaddrinfo(host, port, family, type, proto, flags)

    def getquerylist(self, delims=';&', encoding='utf-8'):
        """Split the query string into individual components using the
        delimiter characters in `delims`, and return a list of `(name,
        value)` pairs.

        """
        qsl = [self.query] if self.query else []
        for delim in delims:
            if isinstance(self.query, bytes) and isinstance(delim, str):
                delim = delim.encode(encoding)
            qsl = [s for qs in qsl for s in qs.split(delim) if s]
        items = []
        for qs in qsl:
            parts = qs.partition(b'=' if isinstance(qs, bytes) else '=')
            name = uridecode(parts[0], encoding)
            value = uridecode(parts[2], encoding) if parts[1] else None
            items.append((name, value))
        return items

    def getquerydict(self, delims=';&', encoding='utf-8'):
        """Split the query string into individual components using the
        delimiter characters in `delims`, and return a dictionary of
        query parameters.

        The dictionary keys are the unique decoded query parameter
        names, and the values are lists of decoded values for each
        name, with names and values seperated by :const:`'='`.
        """
        dict = collections.defaultdict(list)
        for name, value in self.getquerylist(delims, encoding):
            dict[name].append(value)
        return dict

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
    try:
        return SplitResult(*RE.match(string).groups())
    except TypeError:
        # Python 3: handle string as bytes
        groups = RE.match(string.decode('ascii')).groups()
        groups = (None if g is None else g.encode('ascii') for g in groups)
        return SplitResult(*groups)


def uriunsplit(parts):
    """Combine the elements of a five-item iterable into a URI string.

    """
    scheme, authority, path, query, fragment = parts

    # RFC 3986 5.3. Component Recomposition
    try:
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
    except TypeError:
        # Python 3: handle parts as bytes
        parts = (None if p is None else p.decode('ascii') for p in parts)
        return uriunsplit(parts).encode('ascii')


def urijoin(base, ref, strict=False):
    """Convert a URI reference relative to a base URI to its target
    URI string."""
    return uriunsplit(urisplit(base).transform(ref, strict))
