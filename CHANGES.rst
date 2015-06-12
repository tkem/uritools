1.0.0 2015-06-12
----------------

- Fix use of URI references as base URIs in ``urijoin()`` and
  ``SplitResult.transform()``.

- Remove ``SplitResult.getaddrinfo()``.

- Remove ``SplitResult.getauthority()``.

- Remove ``SplitResult.gethostip()``; return ``ipaddress`` address
objects from ``SplitResult.gethost()`` instead.

- Remove ``SplitResult.gethost()`` `encoding` parameter.

- Remove query delimiter parameters.

- Return normalized paths from ``SplitResult.getpath()``.

- Convert character constants to strings.


0.12.0 2015-04-03
-----------------

- Deprecate ``SplitResult.getaddrinfo()``.

- Deprecate ``SplitResult.getauthority()``.

- Deprecate ``SplitResult.gethost()`` and ``SplitResult.gethostip()``
  `encoding` parameter; always use `utf-8` instead.

- Drop support for "bytes-like objects".

- Remove ``DefragResult.base``.


0.11.1 2015-03-25
-----------------

- Fix ``uricompose()`` for relative-path references with colons in the
  first path segment.


0.11.0 2014-12-16
-----------------

- Support `encoding=None` for ``uriencode()`` and ``uridecode()``.

- Add optional `errors` parameter to decoding methods.


0.10.1 2014-11-30
-----------------

- Make ``uricompose()`` return ``str`` on all Python versions.


0.10.0 2014-11-30
-----------------

- Use ``ipaddress`` module for handling IPv4/IPv6 host addresses.

- Add `userinfo`, `host` and `port` keyword arguments to
  ``uricompose()``.

- Deprecate ``DefragResult.base``.

- Feature freeze for `v1.0`.


0.9.0 2014-11-21
----------------

- Improve Python 3 support.


0.8.0 2014-11-04
----------------

- Fix ``uriencode()`` and ``uridecode()``.

- Deprecate ``RE``, ``urinormpath()``, ``DefragResult.getbase()``.

- Support non-string query values in ``uricompose()``.


0.7.0 2014-10-12
----------------

- Add optional port parameter to ``SplitResult.getaddrinfo()``.

- Cache ``SplitResult.authority`` subcomponents.


0.6.0 2014-09-17
----------------

- Add basic IPv6 support.

- Change ``SplitResult.port`` back to string, to distinguish between
  empty and absent port components.

- Remove ``querysep`` and ``sep`` parameters.

- Do not raise ``ValueError`` if scheme is not well-formed.

- Improve Python 3 support.


0.5.2 2014-08-06
----------------

- Fix empty port handling.


0.5.1 2014-06-22
----------------

- Add basic Python 3 support.


0.5.0 2014-06-21
----------------

- Add ``SplitResult.getaddrinfo()``.

- Support query mappings and sequences in ``uricompose()``.


0.4.0 2014-03-20
----------------

- Fix ``SplitResult.port`` to return int (matching urlparse).

- Add ``SplitResult.getquerylist(), SplitResult.getquerydict()``.


0.3.0 2014-03-02
----------------

- Add result object accessor methods.

- Update documentation.


0.2.1 2014-02-24
----------------

- Fix IndexError in ``urinormpath()``.

- Integrate Python 2.7.6 ``urlparse`` unit tests.


0.2.0 2014-02-18
----------------

- Add authority subcomponent attributes.

- Return ``DefragResult`` from ``uridefrag()``.

- Improve edge case behavior.


0.1.0 2014-02-14
----------------

- Initial beta release.
