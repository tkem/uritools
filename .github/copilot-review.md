# Code Review — uritools 7.0.0

**Date:** 2026-11-08
**Reviewed:** `develop` at `ecb30db` ("Prepare v7.0.0.", `__version__` 7.0.0,
changelog section `v7.0.0 (2026-11-08)` with four entries), based on `master` at
`331bca8` (v6.1.5 plus review files). `develop` is in sync with `origin/develop`;
`AGENTS.md` and these review files are uncommitted.

**CI status:** All `tox` environments pass locally on CPython 3.14.4 (`py`: 54 passed,
including `README.rst` and `docs/index.rst` doctests; `pyright` 1.1.414 0 errors,
0 warnings; Sphinx 9.2.0 `-W` clean); run on the same `src/` and `tests/` as `ecb30db`
(only `__version__` differs from the tested tree). GitHub Actions was not checked for
`ecb30db`; other interpreters not run locally.
**Coverage:** 100% line and branch (`src/uritools/__init__.py`).

## Code — Potential Issues

| # | Priority | Location | Finding |
|---|----------|----------|---------|
| 1 | Low | `SplitResult.host` (lines 171–180), `SplitResult.port` (183–189), `_splitauthority()` (652–664) | Three copies of the port rule (*Maintainer Decisions*); `host` drifted once and shipped the `//12345` bug fixed in `a73b146`. A one-line comment at each site naming the other two would make the next edit touch all three. |
| 2 | Info | `# type: ignore` in `tests/` (`test_encoding.py` 83; `test_compose.py` 46, 81, 129, 131, 145, 147, 151, 153, 157, 159, 230, 277, 329; `test_split.py` 319, 321) | Each silences every rule on its line; `# pyright: ignore[reportArgumentType]` would keep the other rules live. Mechanical change. |

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
