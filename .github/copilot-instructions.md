# Copilot Instructions for uritools

Project conventions (stack, commands, code style, architecture constraints, testing,
boundaries and git workflow) live in [`AGENTS.md`](../AGENTS.md). This file adds only
the code review process.

## Code Review

- Reviews **amend `.github/copilot-review.md` in place** (header: date, commit, CI
  status, coverage); never new files, dated sections, a per-commit change summary or
  a list of what was verified (git history is the record).
- Findings are tables ordered High, Medium, Low, Info with columns
  `# | Priority | Location | Finding`; renumber after changes; cross-reference as
  "Code #3". **Resolved issues are removed**, never marked resolved.
- Name the reviewed commit by hash and subject plus its base (`master` at hash). Every
  hash in the review must be an ancestor of the reviewed commit (`git merge-base
  --is-ancestor`); after a rebase or amend replace stale hashes instead of narrating
  history, and drop hashes that survive only in the reflog. When local and
  `origin/develop` differ (`git status -sb` shows ahead/behind), say which was reviewed
  and what differs. List only interpreter versions actually run.
- Keep it brief: under 100 lines, one or two sentences per row, numbers only where
  they decide something, current snapshot only (no comparisons with earlier releases).
  Drop "no issues" sections and Info rows that only restate accepted design. Record
  settled matters under *Maintainer Decisions*. A review changes nothing; fix only
  when asked.
- `CHANGELOG.rst` is reviewed, never edited: entries are imperative one-liners with
  ``double backticks`` and no issue numbers, tagged "(breaking change)" or
  "(potentially breaking change)". A `Prepare vX.Y.Z.` or `Release vX.Y.Z.` commit sets
  `__version__` and the dated `vX.Y.Z (YYYY-MM-DD)` section together and is amended, not
  followed up, until the tag. Every user-visible behavior change needs an entry; docs-only,
  test-only and tooling work is one "Minor/Various ... improvements." or "Update build
  environment." line each; two blank lines between releases.
- Verify before reporting: probe behavior with scripts in both `str` and `bytes`,
  compare parser changes against the previous implementation with a differential test,
  and cross-check `host`/`port` results against `urllib.parse` and `uricompose()`.
- Whatever could not be verified must show up: mark the finding, figure or status as
  unverified where it stands (e.g. "CI not run for this commit", "not run on PyPy")
  and say why. Never state an unchecked claim as fact or leave it out.

## Maintainer Decisions (do not re-raise)

- `getscheme()` and `getfragment()` decode `bytes` input to `str`, like every other
  `get*()` method; the FIXME comments noting the asymmetry stay.
- `gethost()` returns `""` for an empty host with `default=None` (`"file:///"`); an
  empty port matches as `""` and `getport()` returns the default.
- A digits-only authority (`//12345`) is a host; a trailing `:` + ASCII digits is the
  port. `lstrip(b"0123456789")` is used instead of `.isdigit()` so the `str` path does
  not accept Unicode digits.
- The `host` and `port` properties and `_splitauthority()` are three hand-synced
  copies of that rule; a shared helper would cost a Python-level call on the hot path.
- `_get_encoded()` uses `lru_cache` with the default `maxsize=128`; callers cycling
  through more distinct `safe` values rebuild tables but stay bounded.
- `uricompose()` final `.decode()` is narrowed by `assert isinstance(uri, bytes)`;
  `pyright` does not consult the stubs inside the module and no `typing` import is
  wanted in `.py`.
- The `# type: ignore` comments in `tests/` are unscoped and each covers a
  deliberately wrong argument type.
- `SplitResultBytes` / `SplitResultString` are semi-private and stay named as they are.
- `docs/index.rst` documents `DefragResult` and `SplitResult` twice (attribute tables
  under the functions, `autoclass` with `:members:` under "Structured Parse Results").
- `tox -e docs` needs network for the `intersphinx` inventory; not a repository defect.
- A Python version that only joins the CI matrix and classifiers gets no "Add support
  for Python 3.x." changelog line (3.15 in 6.1.4); "Update build environment." covers it.
