"""uritools wrappers for running urlparse unit tests."""

import uritools

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
        return self.userinfo.partition(':')[0] if self.userinfo else None

    @property
    def password(self):
        return self.userinfo.partition(':')[2] if self.userinfo else None

    @property
    def hostname(self):
        return self.host.lower() if self.host else None

    @property
    def port(self):
        port = super(SplitResult, self).port
        if port and int(port) < 65536:
            return int(port)
        if self.host and ':' in self.host:
            return int(self.host.rpartition(':')[2])
        return None

    def geturl(self):
        return urlunsplit(self)


class ParseResult(SplitResult):
    """Wrapper class to adapt uritools.SplitResult to
    urlparse.ParseResult interface."""

    @property
    def path(self):
        return super(ParseResult, self).path.partition(';')[0]

    @property
    def params(self):
        return super(ParseResult, self).path.partition(';')[2]

    def __eq__(self, other):
        return self[:2] + (self.path, self.params) + self[3:] == other

    def __ne__(self, other):
        return self[:2] + (self.path, self.params) + self[3:] != other


def urlsplit(url):
    split = [s or '' for s in uritools.urisplit(url)]
    # urlparse Issue 754016: "path:80" (not RFC3986 compliant)
    if split[0] and not split[1] and split[2].isdigit():
        split[0], split[2] = '', split[0] + ':' + split[2]
    return SplitResult(*split)


def urlunsplit(result):
    scheme, authority, path = result[:3]
    # special handling for "file" scheme
    if scheme == 'file':
        split = [scheme, authority, path]
    else:
        split = [scheme or None, authority or None, path]
    split += [s or None for s in result[3:]]
    return uritools.uriunsplit(split)


def urlparse(url):
    return ParseResult(*urlsplit(url))


def urlunparse(result):
    return urlunsplit(result)


def urljoin(base, url, allow_fragments=True):
    if not base:
        return url
    if not url:
        return base
    # workarounds for RFC 1808/2986 "abnormal" test cases
    if url.startswith('/./') or url.startswith('/../'):
        split = uritools.urisplit(base).transform(url)
        return uritools.uriunsplit(split[:2] + (url, ) + split[3:])
    if url.startswith('../../../../'):
        path = url[url.rfind('/../../'):]
        split = uritools.urisplit(base).transform(url)
        return uritools.uriunsplit(split[:2] + (path, ) + split[3:])
    if url.startswith('../../../'):
        path = url[url.rfind('/../'):]
        split = uritools.urisplit(base).transform(url)
        return uritools.uriunsplit(split[:2] + (path, ) + split[3:])
    return uritools.urijoin(base, url, strict=False)


def urldefrag(url):
    return tuple(s or '' for s in uritools.uridefrag(url))


def parse_qsl(query, keep_blank_values=False):
    split = uritools.urisplit('?' + query.replace('+', ' '))
    if keep_blank_values:
        return [v if v[1] else (v[0], '') for v in split.getquerylist()]
    else:
        return [v for v in split.getquerylist() if v[1]]
