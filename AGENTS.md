# uritools

RFC 3986 URI parsing, classification and composition, replacing the most-used parts of
`urllib.parse`. Pure Python ≥ 3.11, no runtime dependencies, `src/` layout, one module
(`src/uritools/__init__.py`) with inline type stubs (`__init__.pyi`, `py.typed`). Single
maintainer; `master` is the release branch, `develop` is the integration and Dependabot
target. Code reviews follow `.github/copilot-instructions.md`.

## Commands

Run everything through `tox`, never bare `pytest`, `ruff` or `pyright`:

```bash
tox -p auto                                  # all environments, as CI does
tox -e py -- tests/test_split.py -k ipv6     # tests; posargs go to pytest
tox -e pyright,ruff,ruff-format,docs         # stubs, lint, format, Sphinx -W (network)
```

A bare `tox -e py` also runs the `README.rst` and `docs/index.rst` examples
(`--doctest-glob=*.rst`); there is no separate doctest environment. CI (GitHub Actions
on `tkem/uritools`, every push and PR) runs CPython 3.11–3.15, free-threaded 3.13t–3.15t
and PyPy 3.11, then uploads to Codecov; without `gh`, check runs via
`https://api.github.com/repos/tkem/uritools/actions/runs?branch=<branch>`. Green means:
all tests pass, 100% line and branch coverage, `ruff` clean, `pyright` 0 errors and
0 warnings (`reportUnnecessaryTypeIgnoreComment` is an error).

## Code Style

- Every public function takes `str` or `bytes`. Dispatch on the input
  (`if isinstance(uristring, bytes): result = SplitResultBytes` / `else:
  result = SplitResultString`) and apply a change to **both** paths.
- No annotations or `typing` imports in `.py` files; types live in `__init__.pyi`, `str`
  overloads before `bytes` ones, `encoding: None` overloads keyword-only where a
  `default` parameter precedes them. `SplitResult` declares the per-subclass constants
  (`_RE: re.Pattern`, `_EMPTY: str | bytes`, ...) so `pyright` can check the base class.
- Narrow with `assert isinstance(...)` / `assert ... is not None` rather than
  `# type: ignore`; `src/` has none and no file pragma. Tests that pass deliberately
  invalid types add `# type: ignore` only where `pyright` flags the line.
- Docstrings name types in prose (":class:`int`, or `default` if ..."), not in
  signatures. Error messages are capitalized sentences without a period
  (`"Invalid port subcomponent"`, `"Invalid host type: %r" % type(host)`).
- Keep `urisplit()` and `uriencode()` free of avoidable Python-level calls: per-`safe`
  lookup tables come from `_get_encoded()` (`functools.lru_cache`, default `maxsize`),
  and the `host`/`port` properties and `_splitauthority()` each spell out the
  "`:` present and digits-only tail is the port" rule rather than share a helper.
- Docs (`docs/index.rst`, doctested): prose wrapped at column 70, two spaces after a
  sentence, directive bodies indented 3 spaces, single backticks for parameters,
  `:class:`/`:func:`/`:meth:`/`:const:` roles for objects. Keep `README.rst` examples
  in sync with it.

## Architecture Constraints

- Results are `namedtuple` subclasses: tuple access and the `get*()` methods both stay.
  `get*()` methods return `str` (or `ipaddress` objects) unless `encoding=None`.
- `uricompose()` returns `str`; a `str` host is always encoded as UTF-8; a string
  `authority` is split by `_splitauthority()` (last `@`, then a trailing `:` + ASCII
  digits), no regex. Every component raises `TypeError` on a wrong type;
  `uriencode()` accepts `str` and `bytes` only.
- Percent-encoding uses uppercase hex; safe characters per component (`_SAFE_PATH`, ...).
- IP literals go through `ipaddress`; output is bracketed and compressed; IPvFuture
  (`v`/`V` flag, case-insensitive) is rejected with `ValueError`.
- Schemes are case-insensitive: `getscheme()` lowercases, non-strict `urijoin()`
  compares lowered; `uricompose()` produces lowercase.
- The `host` property mirrors `port`: a digits-only authority (`//12345`) is a host.

## Testing

- `unittest.TestCase` with a `check()` helper; one `str` and one `bytes` case per
  input; RFC 3986 examples in `test_rfc3986*()`, edge cases in `test_abnormal()`.
- New behavior needs tests under `tests/` and, if user-visible, docs in
  `docs/index.rst`. Wrong-type inputs assert `TypeError`, wrong values `ValueError`.
- Verify a refactor of a parser against the old implementation with a differential
  test over a small alphabet before trusting the unit tests.
- Scratch scripts (probes, benchmarks, differential tests) go into `.cache/tmp/` in the
  workspace (ignored by git), never `/tmp` or a top-level `tmp/`; remove it when done.

## Boundaries

- Never edit `CHANGELOG.rst` or bump `__version__`; both change only in a
  `Prepare vX.Y.Z.` / `Release vX.Y.Z.` commit, which also dates the changelog section.
- Never add submodules, runtime dependencies, or names to `__all__`; never rename
  `SplitResultBytes` / `SplitResultString` (semi-private by decision).
- Feature requests are not accepted; bug reports require the latest release.
- Do not re-raise the *Maintainer Decisions* in `.github/copilot-instructions.md`.
- Never change `AGENTS.md`, `.github/copilot-instructions.md` or
  `.github/copilot-review.md` in a code PR; they change only in a PR or commit of their own.

## Git

- Branch from `develop`, PR to `develop`; `master` receives releases only. Commit
  subjects are one imperative sentence ending with a period (`Fix RTD version handling.`).
- A new Python version goes into the CI matrix and the `pyproject.toml` classifiers;
  dropping one bumps `requires-python` and is a major release.
- `develop` is rebased and amended freely until release: the `Prepare vX.Y.Z.` commit
  absorbs follow-ups, so hashes change while subjects stay. Refer to commits by subject;
  before citing a hash, check `git status -sb` for ahead/behind and
  `git merge-base --is-ancestor <hash> develop`, and never cite reflog-only hashes.
- Run `tox -p auto` before pushing. A change of convention updates this file in a
  separate, instructions-only PR; keep it under 100 lines.
