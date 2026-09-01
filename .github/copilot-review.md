# Code Review — uritools 6.1.1

**Date:** 2026-05-18  
**CI status:** All green (tox: py, ruff, ruff-format, pyright, docs, doctest)

## Type Stubs (`__init__.pyi`)

No issues. Generic types correctly model both `SplitResultString` and
`SplitResultBytes` via `Generic[AnyStr]`. Overload ordering is correct
for dual-input functions (`str` before `bytes`). Design intent is clear:
`getscheme()`, `getfragment()`, and all `get*()` methods intentionally
return `str` (decoding bytes when needed), and type stubs reflect this.

## Code — Potential Issues

| # | Severity | Location | Finding |
|---|----------|----------|---------|
| 1 | Low | `uriencode()` `_encoded` dict | Cache grows without limit when callers pass arbitrary `safe` values. FIXME at line 79 acknowledges this. Consider `@functools.lru_cache` or dict size cap. |
| 2 | Info | `gethost()` default behavior | Returns `""` when host is empty and `default=None`, but returns `default` when default is not None. Edge case (`"file:///"` → `gethost()` returns `""`) is tested and documented; intentional. |
| 3 | Info | `_AUTHORITY_RE_*` port group | Regex `(?::([0-9]*))?$` captures empty port string for URIs like `http://host:`. Handled correctly downstream (`getport()` returns default for empty port). No bug. |

No implementation bugs found.

## Code — Design Notes

Intentional behaviors and acknowledged trade-offs, in source order. None
require action; the FIXME/TODO comments they refer to are kept deliberately.

| # | Location | Note |
|---|----------|------|
| 1 | `DefragResult.getfragment()`, FIXME line 129 | Decodes to `str` even when `geturi()` returns `bytes`. Consistent with every other `get*()` method; changing it would break the public API. Resolved-by-design. |
| 2 | `getscheme()`, FIXME line 203 | Decodes `bytes` schemes to `str`. `__init__.pyi` types this as `-> str \| None`, confirming intent. |
| 3 | `getauthority()`, TODO line 224 | Calls three separate getters; a single dedicated regex would be faster. Micro-optimization only. |
| 4 | `gethost()` line 243 | Returns `""` for an empty host when `default=None`, but returns `default` otherwise. Asymmetric, but tested and documented (see Potential Issues #2). |
| 5 | `SplitResultBytes` / `SplitResultString`, TODO lines 459 and 498 | Already semi-private (absent from `__all__`). Renaming with a leading underscore would break direct importers for little gain. |
| 6 | `_AUTHORITY_RE_*` lines 620–621 | Empty port matches as `""` rather than `None`. Subtle, but handled downstream (see Potential Issues #3). |

## Tests — Gaps

| # | Priority | Location | Finding |
|---|----------|----------|---------|
| 1 | Low | `uricompose` with `fragment` parameter | Only tested implicitly via RFC 3986 example in `test_rfc3986`. No dedicated test for fragment encoding (e.g., `fragment="foo bar"` → `#foo%20bar`). |
| 2 | Low | `uricompose` with non-default `encoding` | No test passes non-default `encoding` to `uricompose()` (e.g., `encoding="latin-1"` with non-ASCII path). |
| 3 | Low | `uricompose` authority override with bytes | `test_authority_override` only uses `str` values. No test for bytes kwargs to authority subcomponents. |
| 4 | Low | `uriunsplit` with mixed types | Type dispatch uses `path` type to select result class. Mixed types (e.g., str scheme + bytes path) untested; consider documenting behavior. |
| 5 | Low | `DefragResult.getfragment()` default parameter | No test passes non-None `default` to `getfragment()` (e.g., `uridefrag("").getfragment(default="fallback")`). |
| 6 | Low | `getauthority()` with bytes default tuple | `test_encoding_none` tests str/bytes input, but bytes default tuple for `getauthority()` not tested. |

## Docs

| # | Priority | Location | Finding |
|---|----------|----------|---------|
| 1 | Low | `uriencode`/`uridecode` parameter docs | `docs/index.rst` describes input/output types but omits individual parameter docs for `encoding`, `errors`, `safe`. Users must read function signature. |
| 2 | Info | `SplitResult` attribute table | Empty `Index` cells for properties (`userinfo`, `host`, `port`). Intentional (not tuple fields), but could clarify with "n/a". |
| 3 | Low | `master_doc` deprecated | Deprecated in Sphinx 4.0+ in favor of `root_doc`. Works fine currently but will eventually warn. |
| 4 | Info | `DefragResult` / `SplitResult` duplication | Documented twice: inline attribute tables in "URI Decomposition" + `.. autoclass::` in "Structured Parse Results". Provides best reference coverage. |
| 5 | Info | Changelog format | Documented in `copilot-instructions.md` (imperative mood bullets, `vX.Y.Z (YYYY-MM-DD)` headers with `===`). No separate `CONTRIBUTING.md`, but guidance is clear. |
