# Copilot Instructions for uritools

RFC 3986 URI parsing, classification and composition. Pure Python ≥ 3.10, no runtime
dependencies, one module (`src/uritools/__init__.py`) plus stubs (`__init__.pyi`).
Single maintainer; `master` = releases, `develop` = integration and Dependabot target.

## Commands

```bash
tox                                              # everything; CI runs exactly this
tox -e py -- tests/test_split.py -k ipv6         # tests; posargs go to pytest
tox -e ruff,ruff-format,pyright,docs,doctest     # lint, format, types, Sphinx -W (network)
PYTHONPATH=src python3 -m pytest tests/          # without tox (tests src, not site-packages)
PYTHONPATH=src python3 -m doctest README.rst     # README examples; tox does not run them
```

Green means: all tests pass, 100% line and branch coverage, `ruff` clean, `pyright` 0
errors and 0 warnings. `SplitResult` declares the per-subclass constants (`_RE`, ...)
for `pyright`; the two `fullmatch(...).groups()` and the final `.decode()` in
`uricompose()` end with `# type: ignore`; no guards, no file pragma. Unused ignores error.

## Code style

Every public function takes `str` or `bytes`. Dispatch on the input; change both paths:

```python
if isinstance(uristring, bytes):
    result = SplitResultBytes
else:
    result = SplitResultString
```

No function annotations or `typing` imports in `.py`; types live in `__init__.pyi`
(`str` overloads before `encoding: None` ones). Tests with deliberately invalid types add
`# type: ignore` only where `pyright` flags it. Docstrings name types in prose:

```python
"""Return the port subcomponent of the URI authority as an
:class:`int`, or `default` if the original URI reference did
not contain a port or if the port was empty.

"""
```

Tests: `unittest.TestCase` with a `check()` helper, one `str` and one `bytes` case per
input, RFC 3986 examples in `test_rfc3986*()`, edge cases in `test_abnormal()`:

```python
cases = [
    ("//example.com:42", "example.com:42"),
    ("//example.com:42", b"example.com:42"),
]
for uri, authority in cases:
    self.check(uri, authority=authority)
```

Docs (`docs/index.rst`): prose wrapped at column 70, two spaces after a sentence,
directive bodies indented 3 spaces, single backticks for parameters, roles for objects:

```rst
.. autofunction:: uricompose

   All components may be specified as either Unicode strings, which
   will be encoded according to `encoding`, or :class:`bytes` objects.
```

Changelog entry (release commits only, subject `Release v6.1.4.`): `- Improve unit tests.`

## Architecture constraints

- Results are `namedtuple` subclasses: tuple access and `get*()` methods both stay
- `get*()` methods return `str` (or `ipaddress` objects) unless `encoding=None`
- `uricompose()` returns `str`; a `str` host is always encoded as UTF-8; only `authority`,
  `host` and `query` check their type (`TypeError`), other components rely on the stubs
- Percent-encoding uses uppercase hex; safe characters per component (`_SAFE_PATH`, ...)
- IP literals via `ipaddress`; output bracketed and compressed; IPvFuture (`v`/`V`) rejected
- Schemes are case-insensitive: `getscheme()` lowercases, non-strict `urijoin()` compares lowered
- Hot path: no avoidable Python-level calls in `urisplit()` / `uriencode()`

## Boundaries

- Never edit `CHANGELOG.rst` or `__version__`; both change in release commits only
- Never add submodules, runtime dependencies, or names to `__all__`
- Never rename `SplitResultBytes` / `SplitResultString`; semi-private by decision
- Never "fix" these; they are tested, documented and decided: `getscheme()` and
  `getfragment()` decode `bytes` input to `str`; `gethost()` returns `""` for an empty
  host with `default=None`; an empty port matches as `""` and `getport()` returns the
  default; `_encoded` grows per `safe` value; the FIXME/TODO comments stay
- Feature requests are not accepted; bug reports require the latest release
- Keep this file under 100 lines; change it in the same PR as the convention

## Git

- Branch from `develop`, PR to `develop`; `master` receives releases only
- Commit subject: one imperative sentence ending with a period (`Fix RTD version handling.`)
- New Python version: add it to the CI matrix and the `pyproject.toml` classifiers
- Reviews amend `.github/copilot-review.md` in place: header (date, commit, CI, coverage,
  one *Verified* paragraph), tables `# | Priority | Location | Finding` ordered
  High → Info and renumbered, resolved rows removed; a review changes no code
