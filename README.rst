************************************************************************
uritools
************************************************************************

.. image:: https://pypip.in/v/uritools/badge.png
    :target: https://pypi.python.org/pypi/uritools/
    :alt: Latest PyPI version

.. image:: https://pypip.in/d/uritools/badge.png
    :target: https://pypi.python.org/pypi/uritools/
    :alt: Number of PyPI downloads

This module defines RFC 3986 compliant replacements for the most
commonly used functions of the Python Standard Library ``urlparse``
module.

For various reasons, the ``urlparse`` module is not compliant with
current Internet standards, does not include Unicode support, and is
generally unusable with proprietary URI schemes.  As stated in
`Lib/urlparse.py
<http://hg.python.org/cpython/file/2.7/Lib/urlparse.py>`_::

    RFC 3986 is considered the current standard and any future changes
    to urlparse module should conform with it.  The urlparse module is
    currently not entirely compliant with this RFC due to defacto
    scenarios for parsing, and for backward compatibility purposes,
    some parsing quirks from older RFCs are retained.

The ``uritools`` module aims to provide fully RFC 3986 compliant
replacements for some commonly used functions found in ``urlparse``,
plus additional functions for handling Unicode, normalizing URI paths,
and conveniently composing URIs from their individual components.


Installation
========================================================================

To install uritools using pip::

    pip install uritools


Project Resources
========================================================================

- `Documentation <http://pythonhosted.org/uritools/>`_
- `Source code <https://github.com/tkem/uritools>`_
- `Issue tracker <https://github.com/tkem/uritools/issues>`_


Changelog
========================================================================


v0.0.5 (2014-02-09)
------------------------------------------------------------------------

- Add urijoin().
- Improve unit tests.


v0.0.4 (2014-02-09)
------------------------------------------------------------------------

- Add default parameters.
- Improve RFC 3986 compliance.
- Adapt unit tests from urlparse.
- Write some documentation.


v0.0.3 (2014-02-08)
------------------------------------------------------------------------

- Add character encoding parameters.


v0.0.2 (2014-02-08)
------------------------------------------------------------------------

- Add basic unit tests.


v0.0.1 (2014-02-08)
------------------------------------------------------------------------

- Initial alpha release.
