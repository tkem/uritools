# uritools Project Guidelines

## Project Overview

**uritools** is a RFC 3986 compliant URI parsing library that serves as a replacement for Python's `urllib.parse`. The entire implementation is in a single monolithic file (`src/uritools/__init__.py`, ~800 lines) with no submodules.

Key architectural decisions:
- **Single-file design**: All functionality in `__init__.py` (encoding, splitting, composing, classifying)
- **Dual type support**: All functions handle both `str` and `bytes` uniformly via `SplitResultString` and `SplitResultBytes` subclasses
- **Strict RFC 3986 compliance**: Unlike `urllib.parse`, this implementation prioritizes standards adherence over backward compatibility

## Core Architecture

### Type Handling Pattern
The codebase uses parallel implementations for strings and bytes:
```python
# Example from urisplit()
if isinstance(uristring, bytes):
    result = SplitResultBytes  # Uses b"/" separators
else:
    result = SplitResultString  # Uses "/" separators
```

Always maintain this dual-type pattern when adding new functionality. Test both `str` and `bytes` inputs.

### Named Tuple Results
Functions return specialized named tuples (`SplitResult`, `DefragResult`) with rich methods:
- Basic tuple interface: `scheme, authority, path, query, fragment = urisplit(uri)`
- Decoded getters: `.gethost()`, `.getport()`, `.getquery()`
- Classification: `.isuri()`, `.isabspath()`, `.isrelpath()`

When modifying these classes, preserve both the tuple interface and getter methods.

### Encoding Strategy
- `uriencode()` uses cached lookup tables (`_encoded` dict) for performance
- Always percent-encode with uppercase hex digits (RFC 3986 requirement)
- "Safe" characters vary by component (`_SAFE_PATH`, `_SAFE_QUERY`, etc.)

## Development Workflows

### Running Tests
```bash
# Run all tests with coverage (recommended)
tox

# Run specific Python version
tox -e py312

# Run tests directly with pytest
pytest tests/ --cov=uritools --cov-report=term-missing

# Run single test file
pytest tests/test_split.py -v
```

### Code Quality Checks
```bash
# Linting (flake8 with black, bugbear, import-order plugins)
tox -e flake8

# Documentation build
tox -e docs

# Doctest examples
tox -e doctest

# Manifest check
tox -e check-manifest
```

### Building and Installing
```bash
# Install in editable mode for development
pip install -e .

# Build distribution
python -m build
```

## Testing Conventions

### Test Structure Pattern
All test files follow this pattern (see `tests/test_split.py`, `tests/test_compose.py`):
```python
class OperationTest(unittest.TestCase):
    def check(self, expected, actual_or_kwargs):
        # Helper that asserts and provides detailed error messages
        self.assertEqual(...)
    
    def test_rfc3986(self):
        # Test cases directly from RFC 3986 examples
    
    def test_abnormal(self):
        # Edge cases: empty strings, malformed URIs
```

- Use `unittest` framework (not pytest-style)
- Include both `str` and `bytes` variants of each test case
- Test RFC 3986 examples explicitly (helps prove compliance)
- Test edge cases separately in `test_abnormal()` methods

### Coverage Expectations
- Maintain ~95%+ coverage (check with `--cov-report=term-missing`)
- Missing coverage is typically exceptional error paths

## Project-Specific Patterns

### Regex Usage
- Core parsing uses verbose regex with named groups (see `SplitResult.RE`)
- Append B suffix for bytes patterns: `rb"..."` vs `r"..."`
- Use `re.VERBOSE` for readability in complex patterns

### Component Validation
When composing URIs (`uricompose()`):
- Scheme must match `[A-Za-z][A-Za-z0-9+.-]*` and gets lowercased
- Path with authority must start with `/` or be empty
- Path without authority cannot start with `//`
- Relative paths with `:` in first segment need `./` prefix

### IPv6 and IP Address Handling
- Use `ipaddress` module for parsing/validation
- IPv6 addresses are bracketed: `[2001:db8::1]`
- Reject IPvFuture addresses (those starting with `v`)
- Always use compressed form for output

## Common Pitfalls

1. **Don't create submodules**: v4.0.0 removed `chars`, `classify`, `compose`, etc. Everything goes in `__init__.py`

2. **Handle both types**: When adding functions, implement for both `str` and `bytes`, not just strings

3. **Preserve API stability**: Public API defined in `__all__` - changes here are breaking

4. **Dot-segment removal**: The `__remove_dot_segments()` algorithm is subtle and RFC-mandated - test carefully if modifying

5. **Query dict/list handling**: `uricompose()` accepts query as string, dict, or list of tuples - preserve all three modes

## Documentation

- Docstrings follow Google/NumPy style
- Include type hints in descriptions (this predates widespread Python type annotations)
- Build docs with Sphinx: `tox -e docs` (output in `.tox/docs/html`)
- README.rst examples should be executable doctest code

## Dependencies

**Runtime**: None (Python stdlib only)  
**Development**: pytest, pytest-cov, tox, sphinx, flake8 plugins, check-manifest

Avoid adding new dependencies unless absolutely necessary - stdlib-only is a project principle.
