v2.0.0 (2016-10-09)
-------------------

- Drop Python 3.2 support (breaking change).

- No longer treat semicolons as query separators by default (breaking
  change).

- Add optional ``sep`` parameter to ``SplitResult.getquerydict()`` and
  ``SplitResult.getquerylist()`` (breaks ``encoding`` when passed as
  positional argument).

- Add optional ``querysep`` parameter to ``uricompose()`` (breaks
  ``encoding`` when passed as positional argument).


v1.0.2 (2016-04-08)
-------------------

- Fix ``uriencode()`` documentation and unit tests requiring the
  ``safe`` parameter to be a ``bytes`` object.


v1.0.1 (2015-07-09)
-------------------

- Encode semicolon in query values passed to ``uricompose()``.


v1.0.0 (2015-06-12)
-------------------

- Fix use of URI references as base URIs in ``urijoin()`` and
  ``SplitResult.transform()``.

- Remove ``SplitResult.getaddrinfo()``.

- Remove ``SplitResult.getauthority()``.

- Remove ``SplitResult.gethostip()``; return ``ipaddress`` address
objects from ``SplitResult.gethost()`` instead.

- Remove ``SplitResult.gethost()`` ``encoding`` parameter.

- Remove query delimiter parameters.

- Return normalized paths from ``SplitResult.getpath()``.

- Convert character constants to strings.


v0.12.0 (2015-04-03)
--------------------

- Deprecate ``SplitResult.getaddrinfo()``.

- Deprecate ``SplitResult.getauthority()``.

- Deprecate ``SplitResult.gethost()`` and ``SplitResult.gethostip()``
  ``encoding`` parameter; always use ``utf-8`` instead.

- Drop support for "bytes-like objects".

- Remove ``DefragResult.base``.


v0.11.1 (2015-03-25)
--------------------

- Fix ``uricompose()`` for relative-path references with colons in the
  first path segment.


v0.11.0 (2014-12-16)
--------------------

- Support ``encoding=None`` for ``uriencode()`` and ``uridecode()``.

- Add optional ``errors`` parameter to decoding methods.


v0.10.1 (2014-11-30)
--------------------

- Make ``uricompose()`` return ``str`` on all Python versions.


v0.10.0 (2014-11-30)
--------------------

- Use ``ipaddress`` module for handling IPv4/IPv6 host addresses.

- Add ``userinfo``, ``host`` and ``port`` keyword arguments to
  ``uricompose()``.

- Deprecate ``DefragResult.base``.

- Feature freeze for v1.0.


v0.9.0 (2014-11-21)
-------------------

- Improve Python 3 support.


v0.8.0 (2014-11-04)
-------------------

- Fix ``uriencode()`` and ``uridecode()``.

- Deprecate ``RE``, ``urinormpath()``, ``DefragResult.getbase()``.

- Support non-string query values in ``uricompose()``.


v0.7.0 (2014-10-12)
-------------------

- Add optional port parameter to ``SplitResult.getaddrinfo()``.

- Cache ``SplitResult.authority`` subcomponents.


v0.6.0 (2014-09-17)
-------------------

- Add basic IPv6 support.

- Change ``SplitResult.port`` back to string, to distinguish between
  empty and absent port components.

- Remove ``querysep`` and ``sep`` parameters.

- Do not raise ``ValueError`` if scheme is not well-formed.

- Improve Python 3 support.


v0.5.2 (2014-08-06)
-------------------

- Fix empty port handling.


v0.5.1 (2014-06-22)
-------------------

- Add basic Python 3 support.


v0.5.0 (2014-06-21)
-------------------

- Add ``SplitResult.getaddrinfo()``.

- Support query mappings and sequences in ``uricompose()``.


v0.4.0 (2014-03-20)
-------------------

- Fix ``SplitResult.port`` to return int (matching urlparse).

- Add ``SplitResult.getquerylist(), SplitResult.getquerydict()``.


v0.3.0 (2014-03-02)
-------------------

- Add result object accessor methods.

- Update documentation.


v0.2.1 (2014-02-24)
-------------------

- Fix IndexError in ``urinormpath()``.

- Integrate Python 2.7.6 ``urlparse`` unit tests.


v0.2.0 (2014-02-18)
-------------------

- Add authority subcomponent attributes.

- Return ``DefragResult`` from ``uridefrag()``.

- Improve edge case behavior.


v0.1.0 (2014-02-14)
-------------------

- Initial beta release.
