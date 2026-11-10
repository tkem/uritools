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
- Name the reviewed tree by its base commit (hash and subject, release tag if any)
  plus "this review commit", never by the review commit's own hash, which changes
  with every rebase. Cite unreleased commits by subject only; a hash is for the base
  and for ancestors of a release tag, and must be an ancestor of that base
  (`git merge-base --is-ancestor`). Re-check every hash and the "N commits ahead" count
  on each update, even when no code changed: replace stale ones instead of narrating
  history, and drop hashes that survive only in the reflog. When local and
  `origin/develop` differ (`git status -sb` shows ahead/behind), say which was reviewed
  and what differs. List only interpreter versions actually run on this machine, and
  name the commit a GitHub Actions result belongs to if the base has no run of its own.
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
  environment." line each; a new or dropped Python version is "Add support for Python
  3.x." or "Drop Python 3.x support (breaking change)."; two blank lines between releases.
- Verify before reporting: probe behavior with scripts in both `str` and `bytes`,
  compare parser changes against the previous implementation with a differential test,
  and cross-check `host`/`port` results against `urllib.parse` and `uricompose()`.
  Probe scripts go into `.cache/tmp/` in the workspace (ignored by git), never under
  `/tmp` or a top-level `tmp/`; remove `.cache/tmp/` when done.
- The *Performance* section lists ns per call (`timeit`, best of 7) against
  `urllib.parse`: name the interpreter, the machine, the noise and whether the core was
  pinned, take the whole table from one run, and verify a proposed fast path by
  differential test. Re-measure when the interpreter or machine changes; never carry
  figures over from another one. Never update the table from results measured in a VM
  (`systemd-detect-virt` must print `none`): keep the existing table and say so.
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
- `gethost()` and `_host()` call `ipaddress` only after a cheap necessary check (leading
  digit, `:` in the host), and `getpath()` removes dot-segments only if the path has
  `/.` or a leading `.`; the guards are deliberate fast paths, not redundant checks.
- `uricompose()` final `.decode()` is narrowed by `assert isinstance(uri, bytes)`;
  `pyright` does not consult the stubs inside the module and no `typing` import is
  wanted in `.py`.
- The `# type: ignore` comments in `tests/` are unscoped and each covers a
  deliberately wrong argument type.
- `SplitResultBytes` / `SplitResultString` are semi-private and stay named as they are.
- `docs/index.rst` documents `DefragResult` and `SplitResult` twice (attribute tables
  under the functions, `autoclass` with `:members:` under "Structured Parse Results").
- `tox -e docs` needs network for the `intersphinx` inventory; not a repository defect.
- A decision here that a tagged release contradicts is stale: correct the decision and
  say so, rather than report the release.
