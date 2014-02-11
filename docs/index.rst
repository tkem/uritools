.. uritools documentation master file, created by
   sphinx-quickstart on Mon Feb 10 09:15:34 2014.

:mod:`uritools` --- RFC 3986 compliant replacement for :mod:`urlparse`
=======================================================================

.. module:: uritools

This module defines fully RFC 3986 compliant replacements for the most
commonly used functions of the Python Standard Library :mod:`urlparse`
module.

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


Additional URI Functions
------------------------------------------------------------------------

.. autofunction:: uriencode
.. autofunction:: uridecode
.. autofunction:: urinormpath
.. autofunction:: uricompose

Results of :func:`urisplit()`
------------------------------------------------------------------------

Result objects from the :func:`urisplit` function are subclasses of
the :class:`namedtuple` type from the :mod:`collections` module.

   +-------------------+-------+--------------------------+----------------------+
   | Attribute         | Index | Value                    | Value if not present |
   +===================+=======+==========================+======================+
   | :attr:`scheme`    | 0     | URL scheme specifier     | :const:`None`        |
   +-------------------+-------+--------------------------+----------------------+
   | :attr:`authority` | 1     | Network location part    | :const:`None`        |
   +-------------------+-------+--------------------------+----------------------+
   | :attr:`path`      | 2     | Hierarchical path        | empty string         |
   +-------------------+-------+--------------------------+----------------------+
   | :attr:`query`     | 3     | Query component          | :const:`None`        |
   +-------------------+-------+--------------------------+----------------------+
   | :attr:`fragment`  | 4     | Fragment identifier      | :const:`None`        |
   +-------------------+-------+--------------------------+----------------------+

.. autoclass:: SplitResult 
   :members:
..   :undoc-members:
