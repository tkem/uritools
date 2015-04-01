:mod:`uritools` --- RFC 3986 compliant replacement for :mod:`urlparse`
=======================================================================

.. module:: uritools

This module defines RFC 3986 compliant replacements for the most
commonly used functions of the Python 2.7 Standard Library
:mod:`urlparse` and Python 3 :mod:`urllib.parse` modules.

.. code-block:: pycon

    >>> from uritools import urisplit, uriunsplit, urijoin, uridefrag
    >>> parts = urisplit('foo://user@example.com:8042/over/there?name=ferret#nose')
    >>> parts
    SplitResultString(scheme='foo', authority='user@example.com:8042',
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
    >>> urisplit('http://www.xn--lkrbis-vxa4c.at/').gethost(encoding='idna')
    'www.ölkürbis.at'

For various reasons, the Python 2 :mod:`urlparse` module is not
compliant with current Internet standards, does not include Unicode
support, and is generally unusable with proprietary URI schemes.
Python 3's :mod:`urllib.parse` improves on Unicode support, but the
other issues still remain.  As stated in `Lib/urllib/parse.py`_::

    FC 3986 is considered the current standard and any future changes
    to urlparse module should conform with it.  The urlparse module is
    currently not entirely compliant with this RFC due to defacto
    scenarios for parsing, and for backward compatibility purposes,
    some parsing quirks from older RFCs are retained.

This module aims to provide fully RFC 3986 compliant replacements for
the most commonly used functions found in :mod:`urlparse`, plus
additional functions for conveniently composing URIs from their
individual components.

.. seealso::

   :rfc:`3986` - Uniform Resource Identifier (URI): Generic Syntax
        The current Internet standard (STD66) defining URI syntax, to
        which any changes to :mod:`uritools` should conform.  If
        deviations are observed, the module's implementation should be
        changed, even if this means breaking backward compatiblity.


URI Parsing
------------------------------------------------------------------------

.. autofunction:: urisplit

   The return value is an instance of a subclass of
   :class:`collections.namedtuple` with the following read-only
   attributes:

   +-------------------+-------+---------------------------------------------+
   | Attribute         | Index | Value                                       |
   +===================+=======+=============================================+
   | :attr:`scheme`    | 0     | URI scheme, or :const:`None` if not present |
   +-------------------+-------+---------------------------------------------+
   | :attr:`authority` | 1     | Authority component,                        |
   |                   |       | or :const:`None` if not present             |
   +-------------------+-------+---------------------------------------------+
   | :attr:`path`      | 2     | Path component, always present but may be   |
   |                   |       | empty                                       |
   +-------------------+-------+---------------------------------------------+
   | :attr:`query`     | 3     | Query component,                            |
   |                   |       | or :const:`None` if not present             |
   +-------------------+-------+---------------------------------------------+
   | :attr:`fragment`  | 4     | Fragment identifier,                        |
   |                   |       | or :const:`None` if not present             |
   +-------------------+-------+---------------------------------------------+
   | :attr:`userinfo`  |       | Userinfo subcomponent of authority,         |
   |                   |       | or :const:`None` if not present             |
   +-------------------+-------+---------------------------------------------+
   | :attr:`host`      |       | Host subcomponent of authority,             |
   |                   |       | or :const:`None` if not present             |
   +-------------------+-------+---------------------------------------------+
   | :attr:`port`      |       | Port subcomponent of authority as a         |
   |                   |       | (possibly empty) string,                    |
   |                   |       | or :const:`None` if not present             |
   +-------------------+-------+---------------------------------------------+

.. autofunction:: uridefrag

   The return value is an instance of a subclass of
   :class:`collections.namedtuple` with the following read-only
   attributes:

   +-------------------+-------+---------------------------------------------+
   | Attribute         | Index | Value                                       |
   +===================+=======+=============================================+
   | :attr:`uri`       | 0     | Absolute URI or relative URI reference      |
   |                   |       | without the fragment identifier             |
   +-------------------+-------+---------------------------------------------+
   | :attr:`fragment`  | 1     | Fragment identifier,                        |
   |                   |       | or :const:`None` if not present             |
   +-------------------+-------+---------------------------------------------+


URI Composition
------------------------------------------------------------------------

.. autofunction:: uricompose

   `authority` must be a tuple of three elements, specifying userinfo,
   host and port, or :const:`None`.

   If `query` is a mapping object or a sequence of two-element tuples,
   it will be converted to a string of `key=value` pairs seperated by
   `delim`.

.. autofunction:: urijoin

    If `strict` is :const:`False`, a scheme in the reference is
    ignored if it is identical to the base URI's scheme.

.. autofunction:: uriunsplit


URI Encoding
------------------------------------------------------------------------

.. autofunction:: uridecode

   If `encoding` is set to :const:`None`, return the percent-decoded
   `obj` as a :class:`bytes` object.  Otherwise, replace any
   percent-encodings and decode `obj` using the codec registered for
   `encoding`, returning a Unicode string.  The default encoding is
   :const:`utf-8`.

   `obj` may be either a Unicode string or a `bytes-like object`_.

.. autofunction:: uriencode

   If `encoding` is set to :const:`None` and `obj` is a `bytes-like
   object`_, replace any characters not in :const:`UNRESERVED` or
   `safe` with their corresponding percent-encodings and return the
   result as a :class:`bytes` object.  Otherwise, encode `obj` using
   the codec registered for `encoding` before replacing any percent
   encodings.  The default encoding is :const:`utf-8`.

   `obj` may be either a Unicode string or a `bytes-like object`_,
   while `safe` must be a :class:`bytes` object containg ASCII
   characters only.


Constants
------------------------------------------------------------------------

.. data:: UNRESERVED

   Unreserved characters specified in RFC 3986 as a :class:`bytes`
   object.

.. data:: RESERVED

   Reserved characters specified in RFC 3986 as a :class:`bytes`
   object.

.. data:: GEN_DELIMS

   General delimiting characters specified in RFC 3986 as a
   :class:`bytes` object.

.. data:: SUB_DELIMS

   Subcomponent delimiting characters specified in RFC 3986 as a
   :class:`bytes` object.


Structured Parse Results
------------------------------------------------------------------------

The result objects from the :func:`urisplit` and :func:`uridefrag`
functions are instances of subclasses of
:class:`collections.namedtuple`.  These objects contain the attributes
described in the function documentation, as well as some additional
convenience methods:

.. autoclass:: SplitResult
   :members:

   Do not try to create instances of this class directly.  Use the
   :func:`urisplit` factory function instead.

.. autoclass:: DefragResult
   :members:

   Do not try to create instances of this class directly.  Use the
   :func:`uridefrag` factory function instead.


.. _Lib/urllib/parse.py: https://hg.python.org/cpython/file/3.4/Lib/urllib/parse.py
.. _bytes-like object: http://docs.python.org/3/glossary.html#term-bytes-like-object
