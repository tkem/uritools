****************************
uritools
****************************

.. image:: https://pypip.in/v/uritools/badge.png
    :target: https://pypi.python.org/pypi/uritools/
    :alt: Latest PyPI version

.. image:: https://pypip.in/d/uritools/badge.png
    :target: https://pypi.python.org/pypi/uritools/
    :alt: Number of PyPI downloads

For various reasons, the Python Standard Library ``urlparse`` module
is not compliant with current Internet standards, does not include
Unicode support, and is generally unusable with proprietary URI
schemes.  As stated in `Lib/urlparse.py
<http://hg.python.org/cpython/file/2.7/Lib/urlparse.py>`_::

    RFC 3986 is considered the current standard and any future changes
    to urlparse module should conform with it.  The urlparse module is
    currently not entirely compliant with this RFC due to defacto
    scenarios for parsing, and for backward compatibility purposes,
    some parsing quirks from older RFCs are retained.

This module aims to provide fully RFC 3986 compliant, Unicode-aware
replacements for the most commonly used functions provided by
``urlparse``.

The ``uritools`` module currently defines the following classes and
functions:


uritools.\ **urisplit**\ (*uristring*)

Split a URI string into a named tuple with five components::

    <scheme>://<authority>/<path>?<query>#<fragment>

The returned object is an instance of ``SplitResult``.


uritools.\ **uriunsplit**\ (*parts*)

Combine the elements of a tuple as returned by ``urisplit()`` into
a complete URI as a string.

The ``parts`` argument can be any five-item iterable.


uritools.\ **urijoin**\ (*base, ref, strict=False*)

Resolve a URI reference relative to a base URI and return the
resulting URI string.


uritools.\ **uricompose**\ (*scheme=None, authority=None, path='',
query=None, fragment=None, encoding='utf-8'*)

Compose a URI string from its components.


*class* uritools.\ **SplitResult**\ (*scheme, authority, path, query, fragment*)

Extend ``namedtuple`` to hold ``urisplit()`` results.

Attributes:
    :scheme: URI scheme or None if not present
    :authority: URI authority component or None if not present
    :path: URI path component, always present but may be empty
    :query: URI query component or None if not present
    :fragment: URI fragment component or None if not present


Changelog
=========


v0.0.5 (2014-02-09)
----------------------------------------

- Add urijoin().
- Improve unit tests.


v0.0.4 (2014-02-09)
----------------------------------------

- Add default parameters.
- Improve RFC 3986 compliance.
- Adapt unit tests from urlparse.
- Write some documentation.


v0.0.3 (2014-02-08)
----------------------------------------

- Add character encoding parameters.


v0.0.2 (2014-02-08)
----------------------------------------

- Add basic unit tests.


v0.0.1 (2014-02-08)
----------------------------------------

- Initial alpha release.
