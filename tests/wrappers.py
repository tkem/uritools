"""uritools wrappers for running urlparse unit tests"""
from __future__ import unicode_literals

import collections
import sys
import uritools

# Python 3 urllib.parse
parse = sys.modules[__name__]


class SplitResult(uritools.SplitResult):
    """Wrapper class to adapt uritools.SplitResult to
    urlparse.SplitResult interface."""

    @property
    def scheme(self):
        return super(SplitResult, self).scheme.lower()

    @property
    def netloc(self):
        return self.authority

    @property
    def username(self):
        userinfo = super(SplitResult, self).userinfo
        if userinfo is None:
            return None
        elif isinstance(userinfo, type('')):
            return userinfo.partition(':')[0]
        else:
            return userinfo.partition(b':')[0]

    @property
    def password(self):
        userinfo = super(SplitResult, self).userinfo
        if userinfo is None:
            return None
        elif isinstance(userinfo, type('')):
            return userinfo.partition(':')[2]
        else:
            return userinfo.partition(b':')[2]

    @property
    def hostname(self):
        if not self.host:
            return None
        elif self.host[0] in ('[', b'['):
            return self.gethost().lower()
        else:
            return self.host.lower()

    @property
    def port(self):
        port = super(SplitResult, self).port
        return int(port) if port and int(port) < 65536 else None

    def geturl(self):
        return urlunsplit(self)


class ParseResult(SplitResult):
    """Wrapper class to adapt uritools.SplitResult to
    urlparse.ParseResult interface."""

    @property
    def path(self):
        path = super(ParseResult, self).path
        if isinstance(path, type('')):
            return path.partition(';')[0]
        else:
            return path.partition(b';')[0]

    @property
    def params(self):
        path = super(ParseResult, self).path
        if isinstance(path, type('')):
            return path.partition(';')[2]
        else:
            return path.partition(b';')[2]

    def __eq__(self, other):
        return self[:2] + (self.path, self.params) + self[3:] == other

    def __ne__(self, other):
        return self[:2] + (self.path, self.params) + self[3:] != other


class DefragResult(uritools.DefragResult):
    """Wrapper class to adapt uritools.DefragResult to
    urlparse.DefragResult interface."""

    @property
    def url(self):
        return super(DefragResult, self).base

    def geturl(self):
        if self.fragment:
            return self.geturi()
        else:
            return self.base


def urlparse(url, scheme=None):
    parts = urlsplit(url, scheme)
    if '[' in parts.gethost() or ']' in parts.gethost():
        raise ValueError('Invalid IP literal')
    return ParseResult(*parts)


def parse_qs(qs, keep_blank_values=False, encoding='utf-8'):
    dict = collections.defaultdict(list)
    for name, value in parse_qsl(qs, keep_blank_values, encoding=encoding):
        dict[name].append(value)
    return dict


def parse_qsl(qs, keep_blank_values=False, encoding='utf-8'):
    if isinstance(qs, type('')):
        uri, blank = '?' + qs.replace('+', ' '), ''
    else:
        uri, blank = b'?' + qs.replace(b'+', b' '), b''
    items = uritools.urisplit(uri).getquerylist(encoding=encoding)
    if keep_blank_values:
        return [item if item[1] else (item[0], blank) for item in items]
    else:
        return [item for item in items if item[1]]


def urlunparse(parts):
    if isinstance(parts, ParseResult):
        return urlunsplit(parts)
    elif isinstance(parts[2], str):
        return urlunsplit(parts[:2] + (';'.join(parts[2:4]),) + parts[4:])
    else:
        return urlunsplit(parts[:2] + (b';'.join(parts[2:4]),) + parts[4:])


def urlsplit(url, scheme=None):
    if scheme and not isinstance(url, type(scheme)):
        raise TypeError('Cannot mix string and byte')
    parts = uritools.urisplit(url)
    parts = (parts[0] or scheme,) + parts[1:]
    return SplitResult(*(s or type(url)() for s in parts))


def urlunsplit(parts):
    scheme, authority, path = parts[:3]
    # special handling for "file" scheme
    if scheme in ('file', b'file'):
        split = [scheme, authority, path]
    else:
        split = [scheme or None, authority or None, path]
    split += [s or None for s in parts[3:]]
    return uritools.uriunsplit(split)


def urljoin(base, url):
    if not base:
        return url
    elif not url:
        return base
    else:
        return uritools.urijoin(base, url, strict=False)


def urldefrag(url):
    return DefragResult(*(s or type(url)() for s in uritools.uridefrag(url)))


def quote(string, safe='/', encoding='utf-8', errors='strict'):
    return uritools.uriencode(string, safe=safe, encoding=encoding)


def quote_from_bytes(bytes, safe='/'):
    if isinstance(bytes, str):
        raise TypeError()
    return uritools.uriencode(bytes, safe=safe, encoding='ascii')


def unquote(string, encoding='utf-8'):
    return uritools.uridecode(string, encoding=encoding)


def unquote_to_bytes(string):
    return bytes(uritools.uridecode(string, encoding='ascii'))


def urlencode(query, doseq=False, safe='', encoding='utf-8'):
    if doseq:
        query = {key: list(map(str, values)) for key, values in query.items()}
    uri = uritools.uricompose(query=query, encoding=encoding)
    return uritools.urisplit(uri).query
