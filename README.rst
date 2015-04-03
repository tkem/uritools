uritools
========================================================================

This module defines RFC 3986 compliant replacements for the most
commonly used functions of the Python 2.7 Standard Library urlparse_
and Python 3 `urllib.parse`_ modules.

.. code-block:: pycon

    >>> from uritools import urisplit, uriunsplit, urijoin, uridefrag
    >>> parts = urisplit('foo://user@example.com:8042/over/there?name=ferret#nose')
    >>> parts
    SplitResult(scheme='foo', authority='user@example.com:8042',
                path='/over/there', query='name=ferret', fragment='nose')
    >>> parts.scheme
    'foo'
    >>> parts.authority
    'user@example.com:8042'
    >>> parts.userinfo
    'user'
    >>> parts.host
    'example.com'
    >>> parts.port
    '8042'
    >>> uriunsplit(parts[:3] + ('name=swallow&type=African', 'beak'))
    'foo://user@example.com:8042/over/there?name=swallow&type=African#beak'
    >>> urijoin('http://www.cwi.nl/~guido/Python.html', 'FAQ.html')
    'http://www.cwi.nl/~guido/FAQ.html'
    >>> uridefrag('http://pythonhosted.org/uritools/index.html#constants')
    DefragResult(uri='http://pythonhosted.org/uritools/index.html',
                 fragment='constants')

For various reasons, the Python 2 urlparse_ module is not compliant
with current Internet standards, does not include Unicode support, and
is generally unusable with proprietary URI schemes.  Python 3's
`urllib.parse`_ improves on Unicode support, but the other issues
still remain.  As stated in `Lib/urllib/parse.py`_::

    RFC 3986 is considered the current standard and any future changes
    to urlparse module should conform with it.  The urlparse module is
    currently not entirely compliant with this RFC due to defacto
    scenarios for parsing, and for backward compatibility purposes,
    some parsing quirks from older RFCs are retained.

This module aims to provide fully RFC 3986 compliant replacements for
some commonly used functions found in urlparse_ and `urllib.parse`_,
plus additional functions for conveniently composing URIs from their
individual components.


Installation
------------------------------------------------------------------------

Install uritools using pip::

    pip install uritools


Project Resources
------------------------------------------------------------------------

.. image:: http://img.shields.io/pypi/v/uritools.svg?style=flat
    :target: https://pypi.python.org/pypi/uritools/
    :alt: Latest PyPI version

.. image:: http://img.shields.io/pypi/dm/uritools.svg?style=flat
    :target: https://pypi.python.org/pypi/uritools/
    :alt: Number of PyPI downloads

.. image:: http://img.shields.io/travis/tkem/uritools/master.svg?style=flat
    :target: https://travis-ci.org/tkem/uritools/
    :alt: Travis CI build status

.. image:: http://img.shields.io/coveralls/tkem/uritools/master.svg?style=flat
   :target: https://coveralls.io/r/tkem/uritools
   :alt: Test coverage

- `Documentation`_
- `Issue Tracker`_
- `Source Code`_
- `Change Log`_


License
------------------------------------------------------------------------

Copyright (c) 2014, 2015 Thomas Kemmer.

Licensed under the `MIT License`_.


.. _urlparse: http://docs.python.org/2/library/urlparse.html
.. _urllib.parse: http://docs.python.org/3/library/urllib.parse.html
.. _Lib/urllib/parse.py: https://hg.python.org/cpython/file/3.4/Lib/urllib/parse.py

.. _Documentation: http://pythonhosted.org/uritools/
.. _Issue Tracker: https://github.com/tkem/uritools/issues/
.. _Source Code: https://github.com/tkem/uritools/
.. _Change Log: https://github.com/tkem/uritools/blob/master/CHANGES.rst
.. _MIT License: http://raw.github.com/tkem/uritools/master/LICENSE
