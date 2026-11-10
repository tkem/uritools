# Code Review — uritools 7.0.0

**Date:** 2026-11-10
**Reviewed:** `develop`, i.e. `6ae542b` ("Skip the failing IP address parses for
registered names."), five commits ahead of `master` at `fdea0d0` ("Add AGENTS.md, update
Copilot instructions and review.", tagged `v7.0.0`), plus this review commit.
`__version__` is still 7.0.0 and the changelog ends at `v7.0.0 (2026-11-08)`; `34b5285`
(`getpath()`), `6ae542b` (`gethost()`, `_host()`) and `d6d672d` (sdist) are unreleased.

**CI status:** `tox -p auto` passes on CPython 3.13.17 (`py`: 54 passed, including
`README.rst` and `docs/index.rst` doctests; `pyright` 1.1.414 0 errors, 0 warnings;
Sphinx 9.2.0 `-W` clean); `py` also passes on 3.11.17 and 3.12.3. GitHub Actions is
green for the base commit on `develop` (all nine matrix jobs); 3.14, 3.15, the
free-threaded builds and PyPy were not run locally.
**Coverage:** 100% line and branch (`src/uritools/__init__.py`).

## Code — Potential Issues

| # | Priority | Location | Finding |
|---|----------|----------|---------|
| 1 | Low | `uridecode()` (line 95), `uridefrag()` (568), `urijoin()` (609), `getquerylist()` (345) | A wrong type still leaks `AttributeError`: `uridecode(42)`, `uridecode(None)`, `uridefrag(42)`, `urijoin("http://a/", 42)` and `getquerylist(sep=42)` all do, while 7.0.0 made `uriencode()` and `uricompose()` raise `TypeError` and `urisplit(42)` raises `TypeError` from `re`. The same `isinstance(..., str)` / `elif not bytes: raise TypeError` pattern as `uriencode()` would finish the job. |
| 2 | Low | `_ip_literal()` (705–709), `_authority()` (683), `__parse_ip_literal()` (490) | Scoped IPv6 addresses pass through `ipaddress` unchecked. `uricompose(host=ipaddress.IPv6Address("fe80::1%eth0"))` and `host="fe80::1%eth0"` return `//[fe80::1%eth0]`, which is not a URI: RFC 3986 3.2.2 `IPv6address` has no zone and `%et` is not `pct-encoded`. `urisplit("//[fe80::1%25eth0]").gethost()` returns an address with `scope_id == "25eth0"`. Rejecting a `scope_id` with `ValueError` in both directions is the conservative fix. |
| 3 | Low | `SplitResult.host` (lines 172–181), `SplitResult.port` (184–190), `_splitauthority()` (660–672) | Three copies of the port rule (*Maintainer Decisions*); `host` drifted once and shipped the `//12345` bug fixed in `a73b146`. A one-line comment at each site naming the other two would make the next edit touch all three. |

## Performance

Hot-path costs on CPython 3.13.17, ns per call, best of 7 (`timeit`, 100 000 calls per
repeat) in a container on an unpinned core: run-to-run noise about ±20%, so only ratios
above 1.5 are meaningful. Inputs: `URI = "http://user@example.com:8042/over/there/index.html?name=ferret&x=1#nose"`
and its `urisplit()` result; `urllib.parse` as reference where a counterpart exists
(`urlsplit()` is shown uncached, since its `lru_cache` makes repeated inputs 75 ns).
The whole table is from one run.

| Operation | `uritools` | `urllib.parse` |
|---|---|---|
| `urisplit(URI)` (regex 600 + namedtuple 140) | 940 | 2200 |
| `geturi()` / `uriunsplit()` | 370 / 760 | 710 |
| `uridefrag(URI)` | 220 | 1900 |
| `gethost()` registered name / IPv4 / IPv6 | 630 / 1400 / 1900 | 240 / 300 / 290 |
| `getport()` / `getscheme()` / `getquery()` | 170 / 90 / 430 | 360 / – / – |
| `getpath()` without / with dot segments | 470 / 1200 | – |
| `getquerylist()` / `getquerydict()` | 2000 / 2100 | 1500 / 1700 |
| `getauthority()` | 1300 | – |
| `urijoin()` relative path / fragment / absolute | 2500 / 2200 / 1900 | 3700 / 2800 / 2000 |
| `uriencode()` 11 chars / 1 KiB / 64 chars UTF-8 | 560 / 17300 / 1700 | 720 / 19900 / 2100 |
| `uridecode()` no escapes / 5 escapes | 370 / 1500 | 120 / 2100 |
| `uricompose()` scheme+host+path / query dict / all components | 3300 / 6700 / 6200 | 550 / 2500 / – |

| # | Priority | Location | Finding |
|---|----------|----------|---------|
| 1 | Info | `uridecode()` (lines 92–104) | A string without `%` still goes through `split`, `join` and the codec round trip: 350 ns against 70 ns for `encode().decode()` alone and 115 ns for `urllib.parse.unquote()`. A `"%" not in uristring` fast path must keep the round trip, since `uridecode("ü", encoding="ascii")` raises today. |
| 2 | Info | `isuri()` and the other classifiers (lines 612–639) | Each runs a full `urisplit()` (800–900 ns) to read one component; a scheme regex alone takes 130 ns. Fine unless called in bulk. |

## Changelog (`CHANGELOG.rst`)

| # | Priority | Location | Finding |
|---|----------|----------|---------|
| 1 | Info | `v7.0.0` host entry | States the cause ("registered names consisting of digits only") but not the visible effect; "`urisplit("//12345").host` was `""`" would tell an affected user what changed. |
| 2 | Info | Unreleased `34b5285`, `6ae542b` | Two speed-ups without behavior change fit none of the one-line categories in `copilot-instructions.md` (docs, tests, tooling); the next `Prepare` commit needs a wording, e.g. cachetools' "Various performance improvements." |

## Docs

| # | Priority | Location | Finding |
|---|----------|----------|---------|
| 1 | Low | `README.rst` *Related Projects* | `rfc3987` last released 1.3.8 in July 2018; `rfc3986` 2.0.0 in January 2022. Listing an unmaintained package without a note misleads a reader choosing a library. |
| 2 | Low | `docs/index.rst` `SplitResult` attribute table | Empty `Index` cells for `userinfo`, `host`, `port` read as missing data; "n/a" or a footnote that these are properties, not tuple fields, removes the ambiguity. |
| 3 | Info | `README.rst` / `docs/index.rst` `urllib.parse` quote | Matches the CPython 3.14 source at `#L22` (checked 2026-11-08) but ends mid-paragraph without an ellipsis. |
