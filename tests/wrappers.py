"""uritools wrappers for running urlparse unit tests."""

import uritools
from urlparse import ParseResult, SplitResult


def urlparse(url):
    split = urlsplit(url)
    path, _, params = split[2].partition(';')
    return ParseResult(split[0], split[1], path, params, *split[3:])


def urlunparse(result):
    if result.params:
        path = result.path + ';' + result.params
    else:
        path = result.path
    return urlunsplit(result[:2] + (path, ) + result[4:])


def urlsplit(url):
    split = [s or '' for s in uritools.urisplit(url)]
    # workaround for urlparse Issue 754016: "path:80"
    if split[0] and not split[1] and split[2].isdigit():
        split[0], split[2] = '', split[0] + ':' + split[2]
    return SplitResult(split[0].lower(), *split[1:])


def urlunsplit(result):
    scheme, authority, path = result[:3]
    if scheme == 'file':
        split = [scheme, authority, path]
    else:
        split = [scheme or None, authority or None, path]
    split += [s or None for s in result[3:]]
    return uritools.uriunsplit(split)


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
