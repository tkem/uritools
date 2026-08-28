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
| 1 | Low | `uriencode()` `_encoded` dict | Cache grows without limit when callers pass arbitrary `safe` values. FIXME at line 79 acknowledges this. Consider `@functools.lru_cache` or dict size cap. In practice, minimal risk. |
| 2 | Info | `gethost()` default behavior | Returns `""` when host is empty and `default=None`, but returns `default` when default is not None. Edge case (`"file:///"` → `gethost()` returns `""`) is tested and documented; intentional. |
| 3 | Info | `_AUTHORITY_RE_*` port group | Regex `(?::([0-9]*))?$` captures empty port string for URIs like `http://host:`. Handled correctly downstream (`getport()` returns default for empty port). No bug. |

No implementation bugs found. Design notes C2–C6 from prior review remain
valid (FIXMEs about bytes return types are intentional; semi-private classes
not in `__all__` are acceptable).

## Tests — Gaps

| # | Priority | Finding |
|---|----------|---------|
| 1 | Low | `uricompose` with `fragment` parameter | Only tested implicitly via RFC 3986 example in `test_rfc3986`. No dedicated test for fragment encoding (e.g., `fragment="foo bar"` → `#foo%20bar`). |
| 2 | Low | `uricompose` with non-default `encoding` | No test passes non-default `encoding` to `uricompose()` (e.g., `encoding="latin-1"` with non-ASCII path). |
| 3 | Low | `uricompose` authority override with bytes | `test_authority_override` only uses `str` values. No test for bytes kwargs to authority subcomponents. |
| 4 | Low | `uriunsplit` with mixed types | Type dispatch uses `path` type to select result class. Mixed types (e.g., str scheme + bytes path) untested; consider documenting behavior. |
| 5 | Low | `DefragResult.getfragment()` default parameter | No test passes non-None `default` to `getfragment()` (e.g., `uridefrag("").getfragment(default="fallback")`). |
| 6 | Low | `getauthority()` with bytes default tuple | `test_encoding_none` tests str/bytes input, but bytes default tuple for `getauthority()` not tested. |

## Docs

| # | Priority | Finding |
|---|----------|---------|
| 1 | Low | `uriencode`/`uridecode` parameter docs | `docs/index.rst` describes input/output types but omits individual parameter docs for `encoding`, `errors`, `safe`. Users must read function signature. |
| 2 | Info | `SplitResult` attribute table | Empty `Index` cells for properties (`userinfo`, `host`, `port`). Intentional (not tuple fields), but could clarify with "n/a". |
| 3 | Low | `docs/conf.py` `master_doc` | Deprecated in Sphinx 4.0+ in favor of `root_doc`. Works fine currently but will eventually warn. |
| 4 | Info | `DefragResult` / `SplitResult` duplication | Documented twice: inline attribute tables in "URI Decomposition" + `.. autoclass::` in "Structured Parse Results". Provides best reference coverage; no action needed. |
| 5 | Info | Changelog format | Documented in `copilot-instructions.md` (imperative mood bullets, `vX.Y.Z (YYYY-MM-DD)` headers with `===`). No separate `CONTRIBUTING.md`, but guidance is clear. |

## Security

No security issues found. The library:
- Does not perform network I/O
- Does not execute or evaluate URI content  
- Properly validates IP literals and rejects IPvFuture
- Uses percent-encoding with uppercase hex digits per RFC 3986
- Handles path traversal (`../`) correctly per RFC 3986 Section 5.2.4
- `test_path_traversal_limits` confirms `../` * 100 cannot escape root

## Summary

The codebase is clean, well-tested (100% coverage, 45 tests, 394 statements),
and fully passing all checks. Key findings by priority:

**Consider addressing:**
1. **C1** (Code #1): Cap `_encoded` dict or switch to `@functools.lru_cache`

**Nice to have:**
2. **T1–T3, T5–T6**: Add test cases for `uricompose` fragment, encoding, bytes authority override, and getter defaults
3. **D1**: Expand `uriencode`/`uridecode` docs to cover parameters individually  
4. **D3**: Rename `master_doc` to `root_doc` in `docs/conf.py`

**No action needed:**
- C2, C3, D2, D4, D5, T4 — documented for awareness
