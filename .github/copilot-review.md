# Code, Tests & Docs Review

**Date:** 2026-05-18
**Version:** 6.1.1
**Python:** 3.13.7
**Scope:** `src/uritools/__init__.py`, `src/uritools/__init__.pyi`, `tests/`, `docs/`, `README.rst`

## Checks Summary

| Check      | Result |
|------------|--------|
| Tests      | 45 passed |
| Coverage   | 100% (394 statements) |
| Lint       | Clean (ruff check) |
| Format     | Clean (ruff format) |
| Type check | 0 errors (pyright) |
| Docs build | OK (sphinx html) |
| Doctests   | 10 passed |

---

## Code Findings

### C1. Unbounded cache growth in `uriencode()` (low risk)

`_encoded` dict grows without limit when callers pass arbitrary `safe` values. The existing FIXME (line 79) acknowledges this. Consider `@functools.lru_cache` or capping the dict size. In practice, the library only uses a handful of fixed `safe` values internally, so risk is low unless users call `uriencode()` directly with dynamic `safe` arguments.

### C2. `DefragResult.getfragment()` always returns `str` (design note)

The FIXME at line 129 notes that `getfragment()` decodes to `str` by default even when `geturi()` returns `bytes`. This is consistent with `SplitResult.getfragment()` and all other `get*()` methods, so changing it would be a breaking API change. The FIXME can be considered resolved or intentional.

### C3. `getscheme()` always returns `str` (design note)

Similar FIXME at line 203: `getscheme()` decodes bytes schemes to `str`. The stub file already types this as `-> str | None`, confirming this is intentional behavior.

### C4. `SplitResultBytes` / `SplitResultString` visibility (minor)

Both classes have a `# TODO: make private?` comment. They are not in `__all__` so they are already semi-private. Making them fully private (prefixing with `_`) would be a minor cleanup but could break users who import them directly.

### C5. `gethost()` returns empty string for empty host

`gethost(default=X)` returns `default` when host is empty *and* default is not None, but returns `""` when default is None. This edge case (`"file:///"` -> `gethost()` returns `""`) is tested and documented, but the asymmetry between `default=None` and `default="x"` may be unexpected.

### C6. `_AUTHORITY_RE_*` port group matches empty string

The regex `(?::([0-9]*))?$` captures an empty port string for URIs like `http://host:`. This is handled correctly downstream (`_port()` returns `b""` for empty port, `getport()` returns default), but the empty-string-vs-None distinction for port is a subtle edge.

### C8. `getauthority()` TODO about efficiency (trivial)

Line 224: `# TODO: this could be much more efficient by using a dedicated regex` — `getauthority()` calls three separate getters. Could be micro-optimized with a single regex, but unlikely to matter in practice.

---

## Test Findings

### Good practices observed
- All public functions tested with both `str` and `bytes` input
- RFC 3986 examples tested exhaustively (Sections 3, 5.4.1, 5.4.2)
- Edge cases and abnormal inputs covered thoroughly
- `check()` helpers enforce round-trip consistency (parse → recompose)
- IPv4, IPv6, IPv4-mapped IPv6, and IPvFuture rejection all tested
- Error cases test `TypeError` vs `ValueError` distinction
- Cross-type `urijoin` (bytes base + str ref, etc.) tested
- 100% line coverage maintained
- Python 3.13 IPv4-mapped address representation change handled in `test_ipv4_mapped_literal` with dual expected values

### T1. `uricompose` with `fragment` parameter

Only tested implicitly via the RFC 3986 example in `test_rfc3986`. No dedicated test for fragment encoding (e.g., `fragment="foo bar"` producing `#foo%20bar`).

### T2. `uricompose` with non-default `encoding`

No test passes a non-default `encoding` to `uricompose()`. For example, composing with `encoding="latin-1"` and non-ASCII path characters.

### T3. `uricompose` authority override with bytes

`test_authority_override` only uses `str` values. No test overrides authority subcomponents with `bytes` kwargs.

### T4. `uriunsplit` with mixed types

The type dispatch in `uriunsplit()` uses `path` type to select the result class. Mixed types (e.g., str scheme + bytes path) could produce unexpected results but are not tested. Consider documenting this as unsupported or adding a guard.

### T5. `DefragResult.getfragment()` default parameter

No test passes a non-None `default` to `DefragResult.getfragment()` (e.g., `uridefrag("").getfragment(default="fallback")`).

### T6. `getauthority` with bytes default tuple

`test_encoding_none` tests str and bytes URI input, but `getauthority()` with a bytes default tuple is not tested.

---

## Documentation Findings

### D3. `docs/index.rst`: no documentation for `uriencode`/`uridecode` parameters

The `uriencode` and `uridecode` docs describe input/output types but do not document the `encoding`, `errors`, or `safe` parameters individually. Users must read the function signature and docstring. Consider adding parameter descriptions.

### D4. `docs/index.rst`: `SplitResult` attribute table missing `Index` for properties

The `urisplit` attribute table has empty `Index` cells for `userinfo`, `host`, and `port`. This is intentional (they are properties, not tuple fields), but it could be clearer with a note like "n/a" or "(property)".

### D6. `docs/conf.py`: `master_doc` deprecated

`master_doc` is deprecated in Sphinx 4.0+ in favor of `root_doc`. Works fine currently but will eventually produce a warning.

### D7. `docs/index.rst`: `DefragResult` and `SplitResult` documented twice

These classes are first described in the "URI Decomposition" section (inline attribute tables) and then again in "Structured Parse Results" via `.. autoclass::` with `:members:`. This provides the best of both worlds (table overview + detailed API), but the duplication could confuse readers scanning for the complete API of these classes.

### D8. Changelog entry format guidance

The `CHANGELOG.rst` format is documented in `copilot-instructions.md` (imperative mood bullets under `vX.Y.Z (YYYY-MM-DD)` headers with `===` underlines). No separate `CONTRIBUTING.md` exists, but the conventions are clear from the instructions file.

---

## Type Stub Findings

### S1. `DefragResult` and `SplitResult` stub inheritance

The stubs declare `DefragResult(NamedTuple, Generic[AnyStr])` and `SplitResult(NamedTuple, Generic[AnyStr])`, but the runtime classes inherit from `collections.namedtuple(...)` (not `typing.NamedTuple`). This is acceptable for type checking purposes since pyright accepts it (0 errors), but it's a divergence from the runtime class hierarchy.

### S2. `gethost()` default parameter type

The stub types `default` as `str | ipaddress.IPv4Address | ipaddress.IPv6Address | None`, but at runtime any value could be passed as default (it's just returned as-is when host is absent). This is appropriate — the stub reflects intended usage, not arbitrary usage.

### S3. `uriencode` overload for str input missing `encoding=None`

The str overload of `uriencode` types `encoding` as `str`, not `str | None`. The bytes overload allows `str | None`. At runtime, passing `encoding=None` to `uriencode` with a str input would fail (can't call `str.encode(None)`), so the stub is correct — but this asymmetry is not obvious.

---

## Security

No security issues found. The library:
- Does not perform network I/O
- Does not execute or evaluate URI content
- Properly validates IP literals and rejects IPvFuture
- Uses percent-encoding with uppercase hex digits per RFC 3986
- Handles path traversal (`../`) correctly per RFC 3986 Section 5.2.4
- `test_path_traversal_limits` confirms `../` * 100 cannot escape root

---

## Summary

The codebase is clean, well-tested (100% coverage), and fully passing all checks. Key findings by priority:

**Consider addressing:**
1. **C1**: Consider capping `_encoded` cache or switching to `lru_cache`

**Nice to have:**
2. **T1-T3**: Add test cases for `uricompose` fragment, encoding, and bytes authority override
3. **C2-C3**: Resolve or remove FIXME comments about bytes return types (behavior is intentional)
4. **D6**: Rename `master_doc` to `root_doc` in `docs/conf.py`

**No action needed:**
- C4, C5, C6, C8, D3, D4, D7, D8, S1-S3, T4-T6 — documented here for awareness
