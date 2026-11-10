# Code Review — uritools 7.0.0

**Date:** 2026-11-10
**Reviewed:** `develop` at `d6d672d` ("Exclude AGENTS.md from source distribution."),
one commit ahead of `master` at `fdea0d0` ("Add AGENTS.md, update Copilot instructions
and review.", tagged `v7.0.0`). `ecb30db` ("Prepare v7.0.0.") sets `__version__` 7.0.0
and the `v7.0.0 (2026-11-08)` changelog section with four entries. `develop` is in sync
with `origin/develop`.

**CI status:** `tox -p auto` passes on CPython 3.13.17 (`py`: 54 passed, including
`README.rst` and `docs/index.rst` doctests; `pyright` 1.1.414 0 errors, 0 warnings;
Sphinx 9.2.0 `-W` clean); `py` also passes on 3.11.17 and 3.12.3. GitHub Actions is
green for this tree on `develop` (all nine matrix jobs); 3.14, 3.15, the free-threaded
builds and PyPy were not run locally.
**Coverage:** 100% line and branch (`src/uritools/__init__.py`).

## Code — Potential Issues

| # | Priority | Location | Finding |
|---|----------|----------|---------|
| 1 | Low | `uridecode()` (line 95), `uridefrag()` (560), `urijoin()` (601), `getquerylist()` (337) | A wrong type still leaks `AttributeError`: `uridecode(42)`, `uridecode(None)`, `uridefrag(42)`, `urijoin("http://a/", 42)` and `getquerylist(sep=42)` all do, while 7.0.0 made `uriencode()` and `uricompose()` raise `TypeError` and `urisplit(42)` raises `TypeError` from `re`. The same `isinstance(..., str)` / `elif not bytes: raise TypeError` pattern as `uriencode()` would finish the job. |
| 2 | Low | `_ip_literal()` (697–701), `_authority()` (675), `__parse_ip_literal()` (482) | Scoped IPv6 addresses pass through `ipaddress` unchecked. `uricompose(host=ipaddress.IPv6Address("fe80::1%eth0"))` and `host="fe80::1%eth0"` return `//[fe80::1%eth0]`, which is not a URI: RFC 3986 3.2.2 `IPv6address` has no zone and `%et` is not `pct-encoded`. `urisplit("//[fe80::1%25eth0]").gethost()` returns an address with `scope_id == "25eth0"`. Rejecting a `scope_id` with `ValueError` in both directions is the conservative fix. |
| 3 | Low | `SplitResult.host` (lines 171–180), `SplitResult.port` (183–189), `_splitauthority()` (652–664) | Three copies of the port rule (*Maintainer Decisions*); `host` drifted once and shipped the `//12345` bug fixed in `a73b146`. A one-line comment at each site naming the other two would make the next edit touch all three. |

## Performance

Hot-path costs on CPython 3.13.17, ns per call, best of 7 (`timeit`, 100 000 calls per
repeat) in a container on an unpinned core: run-to-run noise about ±20%, so only ratios
above 1.5 are meaningful. Inputs: `URI = "http://user@example.com:8042/over/there/index.html?name=ferret&x=1#nose"`
and its `urisplit()` result; `urllib.parse` as reference where a counterpart exists
(`urlsplit()` is shown uncached, since its `lru_cache` makes repeated inputs 75 ns).

| Operation | `uritools` | `urllib.parse` |
|---|---|---|
| `urisplit(URI)` (regex 580 + namedtuple 150) | 900 | 2100 |
| `geturi()` / `uriunsplit()` | 380 / 720 | 700 |
| `uridefrag(URI)` | 280 | 1850 |
| `gethost()` registered name / IPv4 / IPv6 | 1500 / 1700 / 2200 | 310 / 310 / 350 |
| `getport()` / `getscheme()` / `getquery()` | 210 / 100 / 320 | 310 / – / – |
| `getpath()` without / with dot segments | 1030 / 1080 | – |
| `getquerylist()` / `getquerydict()` | 1500 / 2000 | 1500 / 1400 |
| `getauthority()` | 2600 | – |
| `urijoin()` relative path / fragment / absolute | 2400 / 2100 / 2300 | 3600 / 3300 / 1500 |
| `uriencode()` 11 chars / 1 KiB / 64 chars UTF-8 | 440 / 16700 / 1700 | 630 / 16200 / 1700 |
| `uridecode()` no escapes / 5 escapes | 360 / 1500 | 100 / 2600 |
| `uricompose()` scheme+host+path / query dict / all components | 5000 / 8700 / 7000 | 530 / 3200 / – |

| # | Priority | Location | Finding |
|---|----------|----------|---------|
| 1 | Low | `_host()` (lines 704–715) | Every `str`/`bytes` host is first fed to `ipaddress.IPv6Address()`, which raises for a registered name at about 900 ns, so `uricompose()` with a plain host spends a third of its 5.6 µs on a failed parse. An IPv6 text form always contains `:`; guarding the attempt with `b":" in host` cuts the call to 3.6 µs, identical results on 24 host probes (names, IPv4, IPv6 with and without brackets, IPvFuture, empty, non-ASCII). |
| 2 | Low | `gethost()` (lines 258–282) | Same pattern: `ipaddress.IPv4Address()` is tried on every host and raises for a registered name at about 700 ns, so `gethost()` costs 2.0 µs against 0.85 µs with a first-character digit pre-check (an IPv4 literal starts with a digit; `//12345` still reaches the parser and still falls back to a name). Identical results on 24 probes. The TODO at line 271 asks for this. `getauthority()` (2.6 µs) is the sum of its three getters and inherits the saving. |
| 3 | Low | `getpath()` (lines 296–299) | `__remove_dot_segments()` splits and rejoins every path, 1.05 µs for `/over/there/index.html`, which has no dot segment. A dot segment needs `"/."` in the path or a leading `.`; skipping the pass otherwise halves the call (0.5 µs), identical results on 32 probes including `/.hidden/x`, `a..b/c` and `/a./b`. |
| 4 | Info | `uridecode()` (lines 92–104) | A string without `%` still goes through `split`, `join` and the codec round trip: 450 ns against 75 ns for `encode().decode()` alone and 100 ns for `urllib.parse.unquote()`. A `"%" not in uristring` fast path must keep the round trip, since `uridecode("ü", encoding="ascii")` raises today. |
| 5 | Info | `isuri()` and the other classifiers (lines 604–631) | Each runs a full `urisplit()` (750 ns) to read one component; a scheme regex alone takes 130 ns. Fine unless called in bulk. |

## Changelog (`CHANGELOG.rst`)

| # | Priority | Location | Finding |
|---|----------|----------|---------|
| 1 | Info | `v7.0.0` host entry | States the cause ("registered names consisting of digits only") but not the visible effect; "`urisplit("//12345").host` was `""`" would tell an affected user what changed. |

## Docs

| # | Priority | Location | Finding |
|---|----------|----------|---------|
| 1 | Low | `README.rst` *Related Projects* | `rfc3987` last released 1.3.8 in July 2018; `rfc3986` 2.0.0 in January 2022. Listing an unmaintained package without a note misleads a reader choosing a library. |
| 2 | Low | `docs/index.rst` `SplitResult` attribute table | Empty `Index` cells for `userinfo`, `host`, `port` read as missing data; "n/a" or a footnote that these are properties, not tuple fields, removes the ambiguity. |
| 3 | Info | `README.rst` / `docs/index.rst` `urllib.parse` quote | Matches the CPython 3.14 source at `#L22` (checked 2026-11-08) but ends mid-paragraph without an ellipsis. |
