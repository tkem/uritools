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
the most commonly used functions found in :mod:`urlparse` and
:mod:`urllib.parse`, plus additional functions for conveniently
composing URIs from their individual components.

.. seealso::

   :rfc:`3986` - Uniform Resource Identifier (URI): Generic Syntax
        The current Internet standard (STD66) defining URI syntax, to
        which any changes to :mod:`uritools` should conform.  If
        deviations are observed, the module's implementation should be
        changed, even if this means breaking backward compatiblity.


URI Decomposition
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

.. autofunction:: uriunsplit

.. autofunction:: urijoin

    If `strict` is :const:`False`, a scheme in the reference is
    ignored if it is identical to the base URI's scheme.

.. autofunction:: uricompose

   `authority` may be a Unicode string, :class:`bytes` object, or a
   three-item iterable specifying userinfo, host and port
   subcomponents.  If both `authority` and any of the `userinfo`,
   `host` or `port` keyword arguments are given, the keyword argument
   will override the corresponding `authority` subcomponent.

   If `query` is a mapping object or a sequence of two-element tuples,
   it will be converted to a string of `key=value` pairs seperated by
   `delim`.

   The returned value is of type :class:`str`.


URI Encoding
------------------------------------------------------------------------

.. autofunction:: uriencode

   If `uristring` is a :class:`bytes` object, replace any characters
   not in :const:`UNRESERVED` or `safe` with their corresponding
   percent-encodings and return the result as a :class:`bytes` object.
   Otherwise, encode `uristring` using the codec registered for
   `encoding` before replacing any percent encodings.

   Note that `uristring` may be either a Unicode string or a
   :class:`bytes` object, while `safe` must be a :class:`bytes` object
   containg ASCII characters only.

.. autofunction:: uridecode

   If `encoding` is set to :const:`None`, return the percent-decoded
   `uristring` as a :class:`bytes` object.  Otherwise, replace any
   percent-encodings and decode `uristring` using the codec registered
   for `encoding`, returning a Unicode string.


Character Constants
------------------------------------------------------------------------

.. data:: RESERVED

   Reserved characters specified in RFC 3986 as a :class:`bytes`
   object.

.. data:: GEN_DELIMS

   General delimiting characters specified in RFC 3986 as a
   :class:`bytes` object.

.. data:: SUB_DELIMS

   Subcomponent delimiting characters specified in RFC 3986 as a
   :class:`bytes` object.

.. data:: UNRESERVED

   Unreserved characters specified in RFC 3986 as a :class:`bytes`
   object.


Structured Parse Results
------------------------------------------------------------------------

The result objects from the :func:`urisplit` and :func:`uridefrag`
functions are instances of subclasses of
:class:`collections.namedtuple`.  These objects contain the attributes
described in the function documentation, as well as some additional
convenience methods.

.. autoclass:: SplitResult
   :members:
   :exclude-members: gethost, gethostip

   .. method:: gethost(default=None)

      Return the decoded host subcomponent of the URI authority, or
      `default` if the original URI did not contain a host.

   .. method:: gethostip(default=None)

      Return the decoded host subcomponent of the URI authority as a
      string or an :mod:`ipaddress` address object, or `default` if
      the original URI did not contain a host.

.. autoclass:: DefragResult
   :members:


.. _Lib/urllib/parse.py: https://hg.python.org/cpython/file/3.4/Lib/urllib/parse.py
