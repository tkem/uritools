# uritools Project Guidelines

## Overview

RFC 3986 compliant URI parsing library replacing Python's `urllib.parse`. Requires Python >= 3.10, zero runtime dependencies.

- **Single-file design**: Everything in `src/uritools/__init__.py` — do not create submodules
- **Dual type support**: All public functions handle both `str` and `bytes` via `SplitResultString` / `SplitResultBytes`
- **Public API**: Defined in `__all__` — changes are breaking
- **Type stubs**: `src/uritools/__init__.pyi` — keep in sync with runtime API

## Architecture

Functions return `namedtuple` subclasses (`SplitResult`, `DefragResult`) with both tuple access and getter methods (`.gethost()`, `.getport()`, `.getquerydict()`). Preserve both interfaces when modifying.

Encoding uses cached lookup tables (`_encoded` dict) with uppercase hex digits per RFC 3986. Safe characters vary by component (`_SAFE_PATH`, `_SAFE_QUERY`, etc.).

Type dispatch pattern used throughout:
```python
if isinstance(uristring, bytes):
    result = SplitResultBytes
else:
    result = SplitResultString
```

### Composition rules (`uricompose()`)
- Scheme: `[A-Za-z][A-Za-z0-9+.-]*`, lowercased
- Path with authority must start with `/` or be empty
- Path without authority cannot start with `//`
- Relative paths with `:` in first segment get `./` prefix
- Query accepts `str`, `bytes`, `dict`, or list of tuples
- Invalid host types must raise `TypeError`, not leak `AttributeError`

### IP address handling
- Use `ipaddress` module; reject IPvFuture (addresses starting with `v`)
- IPv6 bracketed in output: `[2001:db8::1]`, always compressed form

### Design decisions (intentional — do not "fix")
- `getscheme()` always returns `str` (decodes bytes schemes)
- `getfragment()` and other `get*()` methods decode to `str` by default, even for bytes input
- `gethost()` returns `""` for empty host when `default=None`, but returns `default` when it's not None
- `SplitResultBytes` / `SplitResultString` are semi-private (not in `__all__`)

## Development

### Running checks
```bash
tox              # all environments (recommended)
tox -e py        # tests with coverage
tox -e ruff-format  # formatting (ruff format)
tox -e ruff      # linting (ruff check)
tox -e pyright   # type checking
tox -e docs      # Sphinx HTML build
tox -e doctest   # Sphinx doctest
```

Use `tox` or `PYTHONPATH=src python3 -m pytest tests/` to test against the workspace source (not the system-installed package).

### Testing conventions
- `unittest.TestCase` with `check()` helpers — not pytest-style
- Test both `str` and `bytes` variants of every case
- Test RFC 3986 examples explicitly in `test_rfc3986()` methods
- Edge cases in separate `test_abnormal()` methods
- Maintain 100% line coverage
- Avoid shadowing built-ins (`dict`, `input`) in loop variables

### Documentation
- Sphinx docs in `docs/`, built with `tox -e docs`
- `README.rst` examples must work as doctests
- Docstrings describe types in prose (no type annotations in signatures)
- Directive body content uses 3-space indentation in `docs/index.rst`

### Changelog
- `CHANGELOG.rst` uses `vX.Y.Z (YYYY-MM-DD)` headers with `===` underlines
- Unreleased changes go under `vX.Y.Z (UNRELEASED)`
- Each entry is a `- ` bullet (imperative mood, no trailing period)
