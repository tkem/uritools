uritools
========================================================================

This module defines RFC 3986 compliant replacements for the most
commonly used functions of the Python 2.7 Standard Library
``urlparse`` and Python 3 ``urllib.parse`` modules.

.. code-block:: pycon

    >>> from uritools import uricompose, urijoin, urisplit, uriunsplit
    >>> uricompose(scheme='foo', host='example.com', port=8042,
    ...            path='/over/there', query={'name': 'ferret'},
    ...            fragment='nose')
    'foo://example.com:8042/over/there?name=ferret#nose'
    >>> parts = urisplit(_)
    >>> parts.scheme
    'foo'
    >>> parts.authority
    'example.com:8042'
    >>> parts.getport(default=80)
    8042
    >>> parts.getquerydict().get('name')
    ['ferret']
    >>> urijoin(uriunsplit(parts), '/right/here?name=swallow#beak')
    'foo://example.com:8042/right/here?name=swallow#beak'

For various reasons, the Python 2 ``urlparse`` module is not compliant
with current Internet standards, does not include Unicode support, and
is generally unusable with proprietary URI schemes.  Python 3's
``urllib.parse`` improves on Unicode support, but the other issues still
remain.  As stated in `Lib/urllib/parse.py
<https://hg.python.org/cpython/file/3.5/Lib/urllib/parse.py>`_::

    RFC 3986 is considered the current standard and any future changes
    to urlparse module should conform with it.  The urlparse module is
    currently not entirely compliant with this RFC due to defacto
    scenarios for parsing, and for backward compatibility purposes,
    some parsing quirks from older RFCs are retained.

This module aims to provide fully RFC 3986 compliant replacements for
some commonly used functions found in ``urlparse`` and
``urllib.parse``, plus additional functions for conveniently composing
URIs from their individual components.


Installation
------------------------------------------------------------------------

Install uritools using pip::

    pip install uritools


Project Resources
------------------------------------------------------------------------

.. image:: http://img.shields.io/pypi/v/uritools.svg?style=flat
    :target: https://pypi.python.org/pypi/uritools/
    :alt: Latest PyPI version

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

Copyright (c) 2014-2016 Thomas Kemmer.

Licensed under the `MIT License`_.


.. _Documentation: http://pythonhosted.org/uritools/
.. _Issue Tracker: https://github.com/tkem/uritools/issues/
.. _Source Code: https://github.com/tkem/uritools/
.. _Change Log: https://github.com/tkem/uritools/blob/master/CHANGES.rst
.. _MIT License: http://raw.github.com/tkem/uritools/master/LICENSE
