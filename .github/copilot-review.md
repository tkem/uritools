# Code Review — uritools 7.0.0

**Date:** 2026-11-10
**Reviewed:** `develop` at `b77d6c0` ("Skip the failing IP address parses for registered
names."), three commits ahead of `master` at `fdea0d0` ("Add AGENTS.md, update Copilot
instructions and review.", tagged `v7.0.0`), plus the review commits on top; local and
`origin/develop` are identical. `__version__` is still 7.0.0 and the changelog ends at
`v7.0.0 (2026-11-08)`; "Exclude AGENTS.md from source distribution.", "Skip dot-segment
removal in getpath() when the path cannot contain any." and the base commit are unreleased.

**CI status:** `tox -p auto` passes on CPython 3.14.4, the only interpreter on this
machine (`py`: 54 passed, including `README.rst` and `docs/index.rst` doctests; `pyright`
1.1.414 0 errors, 0 warnings; Sphinx 9.2.0 `-W` clean). GitHub Actions has no run for
the base commit itself; the latest `develop` run (the previous review commit, same `src/`
and `tests/`) is green on all nine matrix jobs. 3.11–3.13, 3.15, the free-threaded
builds and PyPy were not run locally.
**Coverage:** 100% line and branch (`src/uritools/__init__.py`).

## Code — Potential Issues

The two unreleased fast paths match `v7.0.0` on 2.65 million differential cases
(`gethost()` and `uricompose(host=...)` over hosts up to six characters, `getpath()` over
paths up to seven, `str` and `bytes`).

| # | Priority | Location | Finding |
|---|----------|----------|---------|
| 1 | Low | `getpath()` (lines 300–307) | Percent-encoded dot-segments survive normalization: `urisplit("/a/%2E%2E/b").getpath()` returns `/a/../b` (`str` and `bytes`), because dot-segments are removed before decoding. RFC 3986 2.3 makes `%2E` equivalent to `.`, so a caller that maps the "normalized" path onto a file system gets a traversal. Treating `%2e`/`%2E` as `.` in the segment test (and in the fast-path guard) closes it; no test covers the case. |
| 2 | Low | `uridecode()` (line 95), `uridefrag()` (568), `urijoin()` (609), `getquerylist()` (345) | A wrong type still leaks `AttributeError`: `uridecode(42)`, `uridecode(None)`, `uridefrag(42)`, `urijoin("http://a/", 42)` and `getquerylist(sep=42)` all do, while 7.0.0 made `uriencode()` and `uricompose()` raise `TypeError` and `urisplit(42)` raises `TypeError` from `re`. The same `isinstance(..., str)` / `elif not bytes: raise TypeError` pattern as `uriencode()` would finish the job. |
| 3 | Low | `_ip_literal()` (705–709), `_authority()` (683), `__parse_ip_literal()` (490) | Scoped IPv6 addresses pass through `ipaddress` unchecked. `uricompose(host=ipaddress.IPv6Address("fe80::1%eth0"))` and `host="fe80::1%eth0"` return `//[fe80::1%eth0]`, which is not a URI: RFC 3986 3.2.2 `IPv6address` has no zone and `%et` is not `pct-encoded`. `urisplit("//[fe80::1%25eth0]").gethost()` returns an address with `scope_id == "25eth0"`. Rejecting a `scope_id` with `ValueError` in both directions is the conservative fix. |
| 4 | Low | `SplitResult.host` (lines 172–181), `SplitResult.port` (184–190), `_splitauthority()` (660–672) | Three copies of the port rule (*Maintainer Decisions*); `host` drifted once and shipped the `//12345` bug fixed in `a73b146`. A one-line comment at each site naming the other two would make the next edit touch all three. |

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
| `urisplit(URI)` (regex 450 + namedtuple 130) | 660 | 1500 |
| `geturi()` / `uriunsplit()` | 280 / 520 | 540 / 530 |
| `uridefrag(URI)` | 220 | 1500 |
| `gethost()` registered name / IPv4 / IPv6 | 560 / 1100 / 1500 | 250 / 240 / 290 |
| `getport()` / `getscheme()` / `getquery()` | 160 / 66 / 310 | 250 / – / – |
| `getpath()` without / with dot segments | 340 / 850 | – |
| `getquerylist()` / `getquerydict()` | 1500 / 1800 | 990 / 1200 |
| `getauthority()` | 1200 | – |
| `urijoin()` relative path / fragment / absolute | 2300 / 1700 / 1900 | 2600 / 2000 / 2100 |
| `uriencode()` 11 chars / 1 KiB / 64 chars UTF-8 | 420 / 12600 / 1800 | 590 / 16500 / 2200 |
| `uridecode()` no escapes / 5 escapes | 280 / 1000 | 72 / 1600 |
| `uricompose()` scheme+host+path / query dict / all components | 2800 / 5000 / 4500 | 380 / 2200 / – |

| # | Priority | Location | Finding |
|---|----------|----------|---------|
| 1 | Info | `uridecode()` (lines 92–106) | A string without `%` still goes through `split`, `join` and the codec round trip: 280 ns against 41 ns for `encode().decode()` alone and 72 ns for `urllib.parse.unquote()`. A `"%" not in uristring` fast path must keep the round trip, since `uridecode("ü", encoding="ascii")` raises today. |
| 2 | Info | `isuri()` and the other classifiers (lines 612–639) | Each runs a full `urisplit()` (800 ns) to read one component; a scheme regex alone takes 100 ns. Fine unless called in bulk. |

## Changelog (`CHANGELOG.rst`)

| # | Priority | Location | Finding |
|---|----------|----------|---------|
| 1 | Info | `v7.0.0` host entry | States the cause ("registered names consisting of digits only") but not the visible effect; "`urisplit("//12345").host` was `""`" would tell an affected user what changed. |
| 2 | Info | Unreleased `getpath()` and `gethost()` speed-ups | Two speed-ups without behavior change fit none of the one-line categories in `copilot-instructions.md` (docs, tests, tooling); the next `Prepare` commit needs a wording, e.g. cachetools' "Various performance improvements." |

## Docs

| # | Priority | Location | Finding |
|---|----------|----------|---------|
| 1 | Low | `README.rst` *Related Projects* | `rfc3987` last released 1.3.8 in July 2018; `rfc3986` 2.0.0 in January 2022 (PyPI, checked 2026-11-10). Listing an unmaintained package without a note misleads a reader choosing a library. |
| 2 | Low | `docs/index.rst` `SplitResult` attribute table | Empty `Index` cells for `userinfo`, `host`, `port` read as missing data; "n/a" or a footnote that these are properties, not tuple fields, removes the ambiguity. |
| 3 | Info | `README.rst` / `docs/index.rst` `urllib.parse` quote | Matches the CPython 3.14 source at `#L22` (checked 2026-11-10) but ends mid-paragraph without an ellipsis. |
