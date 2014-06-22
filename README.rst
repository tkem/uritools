uritools
========================================================================

This module defines RFC 3986 compliant replacements for the most
commonly used functions of the Python 2.7 Standard Library urlparse_
and Python 3 `urllib.parse` modules.

.. code-block:: pycon

    >>> from uritools import urisplit, uriunsplit, urijoin, uridefrag
    >>> uri = urisplit('foo://example.com:8042/over/there?name=ferret#nose')
    >>> uri
    SplitResult(scheme='foo', authority='example.com:8042', path='/over/there',
                query='name=ferret', fragment='nose')
    >>> uri.scheme
    'foo'
    >>> uri.authority
    'example.com:8042'
    >>> uri.host
    'example.com'
    >>> uri.port
    8042
    >>> uri.geturi()
    'foo://example.com:8042/over/there?name=ferret#nose'
    >>> uriunsplit(uri[:3] + ('name=swallow&type=African', 'beak'))
    'foo://example.com:8042/over/there?name=swallow&type=African#beak'
    >>> urijoin('http://www.cwi.nl/~guido/Python.html', 'FAQ.html')
    'http://www.cwi.nl/~guido/FAQ.html'
    >>> uridefrag('http://pythonhosted.org/uritools/index.html#constants')
    DefragResult(base='http://pythonhosted.org/uritools/index.html',
                 fragment='constants')
    >>> urisplit('http://www.xn--lkrbis-vxa4c.at/').gethost(encoding='idna')
    'www.ölkürbis.at'

For various reasons, the urlparse_ module is not compliant with
current Internet standards, does not include Unicode support, and is
generally unusable with proprietary URI schemes.  As stated in
`Lib/urlparse.py
<http://hg.python.org/cpython/file/2.7/Lib/urlparse.py>`_::

    RFC 3986 is considered the current standard and any future changes
    to urlparse module should conform with it.  The urlparse module is
    currently not entirely compliant with this RFC due to defacto
    scenarios for parsing, and for backward compatibility purposes,
    some parsing quirks from older RFCs are retained.

This module aims to provide fully RFC 3986 compliant replacements for
some commonly used functions found in urlparse_, plus additional
functions for handling Unicode, normalizing URI paths, and
conveniently composing URIs from their individual components.


Installation
------------------------------------------------------------------------

Install uritools using pip::

    pip install uritools


Project Resources
------------------------------------------------------------------------

.. image:: http://img.shields.io/pypi/v/uritools.svg
    :target: https://pypi.python.org/pypi/uritools/
    :alt: Latest PyPI version

.. image:: http://img.shields.io/pypi/dm/uritools.svg
    :target: https://pypi.python.org/pypi/uritools/
    :alt: Number of PyPI downloads

- `Documentation`_
- `Issue Tracker`_
- `Source Code`_
- `Change Log`_


License
------------------------------------------------------------------------

Copyright (c) 2014 Thomas Kemmer.

Licensed under the `MIT License`_.


Known Bugs and Limitations
------------------------------------------------------------------------

This modules does not handle IPv6 host addresses (yet).


.. _urlparse: http://docs.python.org/2/library/urlparse.html
.. _urllib.parse: http://docs.python.org/3/library/urllib.parse.html

.. _Documentation: http://pythonhosted.org/uritools/
.. _Issue Tracker: https://github.com/tkem/uritools/issues/
.. _Source Code: https://github.com/tkem/uritools
.. _Change Log: https://github.com/tkem/uritools/blob/master/Changes
.. _MIT License: http://raw.github.com/tkem/uritools/master/LICENSE
