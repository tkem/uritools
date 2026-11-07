# Code Review — uritools 6.1.5

**Date:** 2026-11-07

**Reviewed:** `develop` at `0c631bc` ("Release v6.1.5."), six commits
ahead of the last-reviewed `facc907` ("Release v6.1.4."): `7eabbde`
(review files only), `40b1790` (`docs/conf.py` only, drops the default
`root_doc = "index"`), `504a94b` ("Bound uriencode() lookup table with
lru_cache()."), `2909370` ("Improve authority string parsing in
uricompose()."), `ad8ab1f` ("Prefer assert() to "type: ignore".") and
`0c631bc` (`__version__` 6.1.4 → 6.1.5 and the `CHANGELOG.rst`
section, nothing else). No stub or docs changes.
Local `develop` is in sync with `origin/develop`.

**CI status:** `tox` passes locally on CPython 3.14.4 (`py` 50 passed;
`pyright` 1.1.414 0 errors, 0 warnings; Sphinx 9.2.0 `-W` clean;
`doctest` 10 passed). `README.rst` doctest passes. GitHub Actions not
re-checked.

**Coverage:** 100% line and branch (401 statements, 188 branches; 392
and 186 at `facc907`).

**Verified:** `504a94b` replaces the `_encoded` dict keyed by `safe`,
and its FIXME, with a 256-entry base table plus `_get_encoded(safe)`
under `functools.lru_cache` (default `maxsize=128`): bounded,
thread-safe, same table contents. `safe` is still normalized to ASCII
`bytes` first, so `"/"` and `b"/"` share an entry; an unhashable `safe`
raises `TypeError` as before. `2909370` replaces the two authority
regexes and their `# type: ignore`s with `_splitauthority()`:
`rpartition` on the last `@`, then on the last `:`, taking the tail as
port only if it is all ASCII digits, else the whole remainder is the
host. An empty port stays `""` (`"host:"` → `//host`). A differential
test against the old regexes agreed on all 66 430 `str` and `bytes`
strings of length 0–5 over `a @ : 1 ] [ \n 9x`. `ad8ab1f` swaps the
last `src/` ignore for `assert isinstance(uri, bytes)` in
`uricompose()` and the `test_getport()` ignore for
`assert result.authority is not None`; alternatives (redeclaring
`_EMPTY: bytes` per subclass, calling `SplitResultBytes(...).geturi()`
directly, `str(uri, "utf-8")`) all still fail `pyright`. `0c631bc`'s
two changelog entries (`lru_cache`, "minor code and test
improvements") cover `504a94b`, `2909370` and `ad8ab1f`. Line numbers
refer to `0c631bc`.

## Type Stubs (`__init__.pyi`)

No issues; unchanged since `c0aee0d`. `Generic[AnyStr]` models both
result types; `str` overloads precede `bytes`, `encoding: None`
overloads are keyword-only where a `default` precedes them. `pyright`
does not consult the stubs inside `__init__.py`, hence the
`assert isinstance` before `.decode()` (line 847).

## Code — Potential Issues

| # | Priority | Location | Finding |
|---|----------|----------|---------|
| 1 | Low | `uricompose()` component type checks (lines 779, 790–793, 801, 827–832, 842) | Only `authority` (787), `host` (681) and `query` (834) raise `TypeError`; `scheme=42`, `userinfo=42`, `path=42`, `fragment=42`, `port=[1]`, `query={1: 2}`, `authority=[42, None, None]` leak `AttributeError` from `uriencode()`/`_scheme()`. Stubs catch misuse; documented as the narrower guarantee. No change unless uniform `TypeError`s are wanted. |
| 2 | Info | `_get_encoded()` (lines 73–78) | `lru_cache(maxsize=128)`; the five `_SAFE_*` constants plus the default use six entries. More than 128 distinct `safe` values thrash but stay bounded. No change. |
| 3 | Info | `_splitauthority()` (lines 650–662) | `lstrip(b"0123456789")` rather than `.isdigit()` keeps the port ASCII-only in the `str` path, matching the old `[0-9]*`. Empty port `""` is emitted as nothing by `_port()` (line 714). No bug. |
| 4 | Info | `gethost()` default (line 256) | Returns `""` for an empty host with `default=None`; tested and documented. |
| 5 | Info | Eight `# type: ignore`, all in `tests/` (`test_compose.py` 77, 125, 127, 141, 143, 257; `test_split.py` 319, 321) | Each passes a deliberately wrong type, so no narrowing can replace it. Unscoped by convention; `# pyright: ignore[<rule>]` would scope them. |

No implementation bugs found.

## Tests — Gaps

No gaps found; every new branch is covered by existing cases.

## Docs

| # | Priority | Location | Finding |
|---|----------|----------|---------|
| 1 | Low | `README.rst` doctests not run by CI | Not included from `docs/index.rst`; `--doctest-glob=README.rst README.rst` on the `pytest` command in `tox.ini` would run them. Passes by hand. |
| 2 | Info | `SplitResult` attribute table (`docs/index.rst`) | Empty `Index` cells for `userinfo`, `host`, `port` (properties, not tuple fields). Intentional. |
| 3 | Info | `DefragResult` / `SplitResult` duplication | Inline tables plus `.. autoclass::` with `:members:`. Best reference coverage. |
| 4 | Info | `tox -e docs` / `doctest` need network | `intersphinx` fetches `docs.python.org/3/objects.inv`; offline with `-W` the build fails. Not a repository defect. |
