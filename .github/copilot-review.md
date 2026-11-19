# Code Review — uritools 7.0.1

**Date:** 2026-11-19
**Reviewed:** `develop` at `453b7ec` ("Release v7.0.1."), five commits ahead of `master`
at `fdea0d0` ("Add AGENTS.md, update Copilot instructions and review.", tagged `v7.0.0`),
plus this review commit; local and `origin/develop` are identical. `__version__` 7.0.1
matches the changelog section `v7.0.1 (2026-11-19)`; the release is not tagged yet and
PyPI still serves 7.0.0 (checked 2026-11-19).

**CI status:** `tox -p auto` passes on CPython 3.14.4, the only interpreter on this
machine (`py`: 54 passed, including `README.rst` and `docs/index.rst` doctests; `pyright`
1.1.414 0 errors, 0 warnings; Sphinx 9.2.0 `-W` clean). GitHub Actions is green for the
base commit on all nine matrix jobs. 3.11–3.13, 3.15, the free-threaded builds and PyPy
were not run locally.
**Coverage:** 100% line and branch (`src/uritools/__init__.py`).

## Code — Potential Issues

Differential tests against `v7.0.0`, `str` and `bytes`: `gethost()` and
`uricompose(host=...)` agree on 1.6 million cases (hosts up to six characters) and
`getpath()` on 1.5 million for paths without `%` (up to eight characters). On 6.1 million
paths with `%`, `getpath()` matches a two-pass reference model for `str`, `bytes` and
`encoding=None`, no result keeps a dot-segment other than the leading `..` of a relative
path, and 21 297 results differ from `v7.0.0`.

| # | Priority | Location | Finding |
|---|----------|----------|---------|
| 1 | Low | `uridecode()` (line 95), `uridefrag()` (589), `urijoin()` (630), `getquerylist()` (362) | A wrong type still leaks `AttributeError`: `uridecode(42)`, `uridecode(None)`, `uridefrag(42)`, `urijoin("http://a/", 42)` and `getquerylist(sep=42)` all do, while 7.0.0 made `uriencode()` and `uricompose()` raise `TypeError` and `urisplit(42)` raises `TypeError` from `re`. The same `isinstance(..., str)` / `elif not bytes: raise TypeError` pattern as `uriencode()` would finish the job. |
| 2 | Low | `_ip_literal()` (726–730), `_authority()` (704), `__parse_ip_literal()` (507) | Scoped IPv6 addresses pass through `ipaddress` unchecked. `uricompose(host=ipaddress.IPv6Address("fe80::1%eth0"))` and `host="fe80::1%eth0"` return `//[fe80::1%eth0]`, which is not a URI: RFC 3986 3.2.2 `IPv6address` has no zone and `%et` is not `pct-encoded`. `urisplit("//[fe80::1%25eth0]").gethost()` returns an address with `scope_id == "25eth0"`. Rejecting a `scope_id` with `ValueError` in both directions is the conservative fix. |
| 3 | Low | `SplitResult.host` (lines 175–184), `SplitResult.port` (187–195), `_splitauthority()` (681–693) | Three copies of the port rule (*Maintainer Decisions*); `host` drifted once and shipped the `//12345` bug fixed in `a73b146`. A one-line comment at each site naming the other two would make the next edit touch all three. |
| 4 | Info | `urijoin()`, `transform()` against `getpath()` (303–324) | The two now disagree on `%2E`: `urijoin("http://a/b/c/d", "%2E%2E/x")` returns `http://a/b/c/%2E%2E/x`, whose `getpath()` is `/b/x`. Literal removal is what RFC 3986 5.2.4 specifies, so this needs a decision or a sentence in the docs, not necessarily code. |

## Performance

Hot-path costs on CPython 3.14.4, ns per call, best of 7 (`timeit`, 100 000 calls per
repeat; 10 000 for 1 KiB), bare metal (Core Ultra 7 155H), pinned to one core with
`taskset`; a second run agreed within 8%, so ratios below 1.2 mean nothing. Inputs:
`URI = "http://user@example.com:8042/over/there/index.html?name=ferret&x=1#nose"` and
its `urisplit()` result; `urllib.parse` as reference where a counterpart exists
(`urlsplit()` is shown uncached, since its `lru_cache` makes repeated inputs 52 ns).
The whole table is from one run.

| Operation | `uritools` | `urllib.parse` |
|---|---|---|
| `urisplit(URI)` (regex 460 + namedtuple 130) | 690 | 1500 |
| `geturi()` / `uriunsplit()` | 280 / 540 | 550 / 540 |
| `uridefrag(URI)` | 220 | 1600 |
| `gethost()` registered name / IPv4 / IPv6 | 550 / 1200 / 1500 | 250 / 240 / 290 |
| `getport()` / `getscheme()` / `getquery()` | 160 / 67 / 300 | 260 / – / – |
| `getpath()` plain / dot-segments / one `%20` / `%2E%2E` segment | 360 / 900 / 670 / 1000 | – |
| `getquerylist()` / `getquerydict()` | 1500 / 1800 | 1000 / 1200 |
| `getauthority()` | 1200 | – |
| `urijoin()` relative path / fragment / absolute | 2400 / 1700 / 2000 | 2700 / 2100 / 2100 |
| `uriencode()` 11 chars / 1 KiB / 64 chars UTF-8 | 420 / 13000 / 1700 | 600 / 16700 / 2200 |
| `uridecode()` no escapes / 5 escapes | 280 / 1000 | 73 / 1600 |
| `uricompose()` scheme+host+path / query dict / all components | 3000 / 5200 / 4600 | 390 / 2200 / – |

| # | Priority | Location | Finding |
|---|----------|----------|---------|
| 1 | Info | `uridecode()` (lines 92–106) | A string without `%` still goes through `split`, `join` and the codec round trip: 280 ns against 42 ns for `encode().decode()` alone and 73 ns for `urllib.parse.unquote()`. A `"%" not in uristring` fast path must keep the round trip, since `uridecode("ü", encoding="ascii")` raises today. |
| 2 | Info | `isuri()` and the other classifiers (lines 633–660) | Each runs a full `urisplit()` (820 ns) to read one component; a scheme regex alone takes 100 ns. Fine unless called in bulk. |

## Changelog (`CHANGELOG.rst`)

| # | Priority | Location | Finding |
|---|----------|----------|---------|
| 1 | Info | `v7.0.0` host entry | States the cause ("registered names consisting of digits only") but not the visible effect; "`urisplit("//12345").host` was `""`" would tell an affected user what changed. |

## Docs

| # | Priority | Location | Finding |
|---|----------|----------|---------|
| 1 | Low | `getpath()` docstring, `docs/index.rst` | Still only "Return the normalized decoded URI path."; neither says that `%2E` counts as `.` or that dot-segments are removed again after decoding. The change is user-visible and has a changelog entry, so it needs a sentence. |
| 2 | Low | `README.rst` *Related Projects* | `rfc3987` last released 1.3.8 in July 2018; `rfc3986` 2.0.0 in January 2022 (PyPI, checked 2026-11-19). Listing an unmaintained package without a note misleads a reader choosing a library. |
| 3 | Low | `docs/index.rst` `SplitResult` attribute table | Empty `Index` cells for `userinfo`, `host`, `port` read as missing data; "n/a" or a footnote that these are properties, not tuple fields, removes the ambiguity. |
| 4 | Info | `README.rst` / `docs/index.rst` `urllib.parse` quote | Matches the CPython 3.14 source at `#L22` (checked 2026-11-19) but ends mid-paragraph without an ellipsis. |
