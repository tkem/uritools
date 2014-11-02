:mod:`uritools` --- RFC 3986 compliant replacement for :mod:`urlparse`
=======================================================================

.. module:: uritools

This module defines RFC 3986 compliant replacements for the most
commonly used functions of the Python 2.7 Standard Library
:mod:`urlparse` and Python 3 :mod:`urllib.parse` modules.

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
    '8042'
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

For various reasons, the :mod:`urlparse` module is not compliant with
current Internet standards, does not include Unicode support, and is
generally unusable with proprietary URI schemes.  As stated in
`Lib/urlparse.py
<http://hg.python.org/cpython/file/2.7/Lib/urlparse.py>`_::

    RFC 3986 is considered the current standard and any future changes
    to urlparse module should conform with it.  The urlparse module is
    currently not entirely compliant with this RFC due to defacto
    scenarios for parsing, and for backward compatibility purposes,
    some parsing quirks from older RFCs are retained.

The :mod:`uritools` module aims to provide fully RFC 3986 compliant
replacements for some commonly used functions found in
:mod:`urlparse`, plus additional functions for handling Unicode,
normalizing URI paths, and conveniently composing URIs from their
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

.. autofunction:: uriunsplit

.. autofunction:: urijoin

.. autofunction:: uridefrag


URI Encoding
------------------------------------------------------------------------

.. autofunction:: uriencode

   This function can be used as a Unicode-aware replacement for
   :func:`urllib.quote`.  Compared to :func:`urllib.quote`, this
   function never encodes the tilde character (`~`), which is an
   unreserved character in RFC 3986, and encodes slash characters by
   default.

   Note that this function should not be confused with
   :func:`urllib.urlencode`, which does something completely
   different.

.. autofunction:: uridecode

   This function can be used as a Unicode-aware replacement for
   :func:`urllib.unquote`.


Additional Functions
------------------------------------------------------------------------

.. autofunction:: urinormpath

.. autofunction:: uricompose


Constants
------------------------------------------------------------------------

.. data:: RE

   Regular expression for splitting a well-formed URI into its
   components, as specified in RFC 3986 Appendix B.

   The matched URI components are available by group index and via
   symbolic group names::

      >>> uri = 'foo://example.com:8042/over/there?name=ferret#nose'
      >>> uritools.RE.match(uri).groups()
      ('foo', 'example.com:8042', '/over/there', 'name=ferret', 'nose')
      >>> uritools.RE.match(uri).groupdict()
      {'fragment': 'nose', 'path': '/over/there', 'scheme': 'foo',
       'authority': 'example.com:8042', 'query': 'name=ferret'}

.. data:: UNRESERVED

   Unreserved characters specified in RFC 3986 as a byte string.

.. data:: RESERVED

   Reserved characters specified in RFC 3986 as a byte string.

.. data:: GEN_DELIMS

   General delimiting characters specified in RFC 3986 as a byte
   string.

.. data:: SUB_DELIMS

   Subcomponent delimiting characters specified in RFC 3986 as a byte
   string.


Structured Parse Results
------------------------------------------------------------------------

The result objects from the :func:`urisplit` and :func:`uridefrag`
functions are instances of subclasses of
:class:`collections.namedtuple`.  These objects contain the attributes
described in the function documentation, as well as some additional
convenience methods:

.. autoclass:: SplitResult
   :members:

.. autoclass:: DefragResult
   :members:
