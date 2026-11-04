# Code Review — uritools 6.1.4

**Date:** 2026-11-04

**Reviewed:** `develop` at `facc907` ("Release v6.1.4."), ten commits
ahead of the last-reviewed `c0aee0d` ("Update copilot-review.md.",
which reviewed v6.1.1). Scope: `36ff44a` (bug report template only),
`3d9212f` and `2b2a96d` (CI/tooling only — Python 3.15 added to the CI
matrix and `pyproject.toml` classifiers, `pyright` config tightened to
`reportUnnecessaryTypeIgnoreComment = "error"`, `pytest-cov` gains
`--cov-branch`), `5f73517` ("Fix newline handling in uricompose() and
urisplit()"), `65fecbb` ("Improve type correctness."), `b146c75`
("Extend and improve various unit tests."), `9ca7b01` ("Compare
schemes case-insensitively in non-strict urijoin()."), `2f21b6d`
("Recognize an uppercase IPvFuture version flag."), `52ffab2` (docs
only), `facc907` (`__version__` 6.1.3 → 6.1.4 and the `CHANGELOG.rst`
section, nothing else). `README.rst` is unchanged since `c0aee0d`, so
its row is carried over. Local `develop` is 3 ahead and 2 behind
`origin/develop` (`65dee88`): `2f21b6d` and `52ffab2` rewrite origin's
`93e8888` and `65dee88`, differing only in the capitalized
`"Address mechanism not supported"` message (line 481), and `facc907`
is not yet pushed. This review covers the local branch.

**CI status:** `tox` (`py`, `docs`, `doctest`, `pyright`, `ruff`,
`ruff-format`) passes locally on CPython 3.14.4 (`py` 50 passed under
pytest 9.2.0; `pyright` 1.1.414 0 errors, 0 warnings; Sphinx 9.2.0
`-W` clean; `doctest` 10 passed). `PYTHONPATH=src python3 -m doctest
README.rst` passes. GitHub Actions not re-checked for this review.

**Coverage:** 100% line and branch coverage of
`src/uritools/__init__.py` (392 statements, 186 branches;
`--cov-branch` was added by `2b2a96d`).

**Verified:** `5f73517` fixes a real bug: unanchored `$` in
`_SCHEME_RE` and `_AUTHORITY_RE_*` let a trailing newline pass
validation (Python's `$`, without `re.MULTILINE`, matches just before
a trailing `\n`), and the `SplitResult` regexes' fragment group
(`(.*)`) excluded embedded newlines without `re.DOTALL`, silently
truncating fragments. Fixed by switching `_scheme()` and the
`uricompose()` authority parsing to `.fullmatch()` with the anchors
removed and adding `re.DOTALL` to all four regexes; `test_compose.py`
(`test_scheme`, `test_authority`) and `test_split.py` (`test_abnormal`)
round-trip embedded-newline cases as both `str` and `bytes`.
`65fecbb` reacts to the stricter `pyright` config: it declares the
per-subclass constants (`_RE: re.Pattern`, `_COLON: str | bytes`, ...)
on `SplitResult`, hoists `_match()` into the base class, and adds the
two `uricompose()` authority `# type: ignore` comments that the
previously-overridden `reportAttributeAccessIssue`/
`reportOptionalMemberAccess` settings had been masking. Removing the
three source ignores on a scratch copy reproduces exactly three errors
(`reportOptionalMemberAccess` at lines 776 and 778,
`reportAttributeAccessIssue` at line 839) and nothing else, so each is
load-bearing. `b146c75` closes all six test gaps from the previous
review (`test_fragment`, `test_encoding`, `test_authority_override`,
`test_mixed_types`, `test_getfragment_default`, `test_getauthority`).
`9ca7b01` makes non-strict `urijoin()` compare schemes with
`.lower()` per RFC 3986 3.1; the added `self.scheme is None` guard
only avoids `None.lower()` and preserves the old result for a
scheme-less base. Checked by hand: `urijoin("HTTP://a/b/c/d;p?q",
"http:g")` → `HTTP://a/b/c/g`, the reverse case → `http://a/b/c/g`,
and `strict=True` → `HTTP:g`; `test_join.py` `test_scheme_case` pins
all three plus `bytes` via `check()`. `2f21b6d` accepts an uppercase
IPvFuture flag in both `__parse_ip_literal()` and `_ip_literal()` per
RFC 3986 3.2.2 (`"v"` is case-insensitive); `[V1.x]` now raises
`ValueError("Address mechanism not supported")` from both `gethost()`
and `uricompose()` instead of a generic `AddressValueError`, as `str`
and `bytes`, and both sites use the same capitalized message as every
other `ValueError`/`TypeError` in the module (lines 236–827).
`52ffab2` resolves the former Docs rows 1–4 (`host` UTF-8 note,
`uriunsplit` prose, `uriencode`/`uridecode` parameter docs,
`root_doc`) and adds a `transform()` note; the new prose matches the
code (`uridecode()` line 95, `uriencode()` lines 75–76,
`_authority()` lines 669–670). `facc907` touches only `__version__`
and `CHANGELOG.rst`, whose six entries match the commits above. The
error-type probe in Code row 1 was run against `src/` by hand. Line
numbers below refer to `HEAD` (`facc907`).

## Type Stubs (`__init__.pyi`)

No issues. Generic types correctly model both `SplitResultString` and
`SplitResultBytes` via `Generic[AnyStr]`. Overload ordering is correct
for dual-input functions (`str` before `bytes`; `encoding: None`
overloads are keyword-only where a `default` parameter precedes them,
positional in `uridecode()` and `getpath()`). Design intent is clear:
`getscheme()`, `getfragment()`, and all `get*()` methods intentionally
return `str` (decoding bytes when needed), and type stubs reflect
this. Note that `pyright` does not consult the stubs while checking
`__init__.py` itself; inside the module every call resolves to the
unannotated `.py` definition, which is why the three source ignores
exist (Code rows 5–6).

## Code — Potential Issues

| # | Priority | Location | Finding |
|---|----------|----------|---------|
| 1 | Low | `uricompose()` component type checks (lines 767–770, 783–788, 794, 820–827, 834–835) | Only `authority` (line 780), `host` (line 672) and `query` (line 827) validate their type and raise `TypeError`. Every other component of the wrong type leaks `AttributeError: 'int' object has no attribute 'encode'` from `uriencode()` or `_scheme()`: `scheme=42`, `userinfo=42`, `path=42`, `path=None`, `fragment=42`, `port=[1]`, `query={1: 2}`, `query=[(1, 2)]` and `authority=[42, None, None]` all do (`port=True` is a `numbers.Number` and raises `ValueError`). The stubs type all of these, so a checker catches misuse; `copilot-instructions.md` *Architecture constraints* states the narrower guarantee. No change unless the maintainer wants uniform `TypeError`s. |
| 2 | Info | `uriencode()` `_encoded` dict (lines 62, 79) | Cache grows without limit when callers pass arbitrary `safe` values; the FIXME at line 79 acknowledges this. Decided in `copilot-instructions.md` *Boundaries*; no change. |
| 3 | Info | `gethost()` default behavior (line 258) | Returns `""` when host is empty and `default=None`, but returns `default` when default is not `None`. Edge case (`"file:///"` → `gethost()` returns `""`) is tested and documented; intentional. |
| 4 | Info | `_AUTHORITY_RE_*` port group (lines 638–639) | Regex `(?::([0-9]*))?` captures an empty port string for URIs like `http://host:`. Handled correctly downstream (`getport()` returns `default` for an empty port). No bug. |
| 5 | Info | `fullmatch(...).groups()` in `uricompose()` (lines 776, 778) | `pyright` reports `"groups" is not a known attribute of "None"` (`reportOptionalMemberAccess`) at both sites, each silenced by `# type: ignore`. `urisplit()`'s `result._match(uristring).groups()` (line 575) needs none: `_match()` (line 428) is an unannotated classmethod reached through a `type[SplitResultBytes] \| type[SplitResultString]` union, so `pyright` infers the call as `Unknown` and reports nothing. All three regexes always match: `SplitResult._RE` is not end-anchored and every group is optional, and the `_AUTHORITY_RE_*` groups are optional with `(.*?)`/`re.DOTALL` absorbing any remainder. No guard needed. |
| 6 | Info | `uricompose()` final `.decode()` (line 839) | `pyright` reports `Cannot access attribute "decode" for class "str"` (`reportAttributeAccessIssue`), hence the `# type: ignore`. Inside the module `uriunsplit()` is the unannotated `.py` function, whose return is inferred from `SplitResult.geturi()` → `self._EMPTY.join(result)` with `_EMPTY: str \| bytes` (line 155), so the call is typed `bytes \| str` regardless of the `bytes`-only `parts` tuple. Narrowing it would need a return annotation or `typing` import in the `.py`; accepted to keep both out. |
| 7 | Info | All twelve `# type: ignore` in the repo (3 in `src/uritools/__init__.py`: lines 776, 778, 839; 9 in `tests/`: `test_compose.py` lines 77, 125, 127, 141, 143, 257, `test_split.py` lines 319, 321, 343) | Unscoped, as documented in `copilot-instructions.md`: each silences every rule on its line. `# pyright: ignore[<rule>]` would keep other rules live if that convention changes. |

No implementation bugs found.

## Tests — Gaps

No gaps found.

## Docs

| # | Priority | Location | Finding |
|---|----------|----------|---------|
| 1 | Low | `README.rst` doctests not run by CI | `README.rst` is not included from `docs/index.rst`, so neither `tox -e doctest` nor `tox -e py` executes its examples. `--doctest-glob=README.rst README.rst` on the `pytest` command in `tox.ini` would. `python3 -m doctest README.rst` passes. |
| 2 | Info | `SplitResult` attribute table (`docs/index.rst`) | Empty `Index` cells for properties (`userinfo`, `host`, `port`). Intentional (not tuple fields), but could clarify with "n/a". |
| 3 | Info | `DefragResult` / `SplitResult` duplication | Documented twice: inline attribute tables in "URI Decomposition" + `.. autoclass::` with `:members:` in "Structured Parse Results". Provides the best reference coverage. |
| 4 | Info | Changelog format | Documented in `copilot-instructions.md`. No separate `CONTRIBUTING.md`, but guidance is clear. |
| 5 | Info | `tox -e docs` / `tox -e doctest` need network | `sphinx.ext.intersphinx` fetches `https://docs.python.org/3/objects.inv`; with `-W`, an unreachable inventory fails the build offline. Not a repository defect. |
