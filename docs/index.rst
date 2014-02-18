:mod:`uritools` --- RFC 3986 compliant replacement for :mod:`urlparse`
=======================================================================

.. module:: uritools

This module defines RFC 3986 compliant replacements for the most
commonly used functions of the Python Standard Library :mod:`urlparse`
module.

.. code-block:: pycon

    >>> from uritools import urisplit, uriunsplit, urijoin, uridefrag
    >>> p = urisplit('foo://example.com:8042/over/there?name=ferret#nose')
    >>> p
    SplitResult(scheme='foo', authority='example.com:8042', path='/over/there',
                query='name=ferret', fragment='nose')
    >>> p.scheme
    'foo'
    >>> p.authority
    'example.com:8042'
    >>> p.geturi()
    'foo://example.com:8042/over/there?name=ferret#nose'
    >>> uriunsplit(['foo', 'example.com:8042', '/over/there', 'name=ferret', 'nose'])
    'foo://example.com:8042/over/there?name=ferret#nose'
    >>> urijoin('http://www.cwi.nl/~guido/Python.html', 'FAQ.html')
    'http://www.cwi.nl/~guido/FAQ.html'
    >>> uridefrag('http://pythonhosted.org/uritools/index.html#uritools.uridefrag')
    ('http://pythonhosted.org/uritools/index.html', 'uritools.uridefrag')

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


Replacement Functions for :mod:`uriparse`
------------------------------------------------------------------------

.. autofunction:: urisplit

.. autofunction:: uriunsplit

.. autofunction:: urijoin

.. autofunction:: uridefrag


Additional Functions
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

.. autofunction:: urinormpath

.. autofunction:: uricompose


Constants
------------------------------------------------------------------------

.. data:: RE

   Regular expression for splitting a well-formed URI into its
   components.

.. autodata:: UNRESERVED

.. autodata:: RESERVED

.. autodata:: GEN_DELIMS

.. autodata:: SUB_DELIMS



Results of :func:`urisplit`
------------------------------------------------------------------------

Result objects from the :func:`urisplit` function are actually
instances of subclasses of :class:`collections.namedtuple`.

.. autoclass:: SplitResult
   :members:
