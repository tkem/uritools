# uritools Project Guidelines

## Overview

RFC 3986 compliant URI parsing library replacing Python's `urllib.parse`. Requires Python >= 3.10, zero runtime dependencies.

- **Single-file design**: Everything in `src/uritools/__init__.py` — do not create submodules
- **Dual type support**: All public functions handle both `str` and `bytes` via `SplitResultString` / `SplitResultBytes`
- **Public API**: Defined in `__all__` — changes are breaking

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

## Development

### Running checks
```bash
tox              # all environments (recommended)
tox -e py        # tests with coverage
tox -e flake8    # linting (black, bugbear, import-order)
tox -e docs      # Sphinx HTML build
tox -e doctest   # Sphinx doctest
```

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
