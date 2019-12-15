***************************************************************
:mod:`uritools` --- URI parsing, classification and composition
***************************************************************

.. module:: uritools

This module provides RFC 3986 compliant functions for parsing,
classifying and composing URIs and URI references, largely replacing
the Python Standard Library's :mod:`urllib.parse` module.

.. doctest::

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
    >>> parts.isuri()
    True
    >>> parts.isabsuri()
    False
    >>> urijoin(uriunsplit(parts), '/right/here?name=swallow#beak')
    'foo://example.com:8042/right/here?name=swallow#beak'

For various reasons, :mod:`urllib.parse` and its Python 2 predecessor
:mod:`urlparse` are not compliant with current Internet standards.  As
stated in `Lib/urllib/parse.py
<https://github.com/python/cpython/blob/3.8/Lib/urllib/parse.py>`_:

    RFC 3986 is considered the current standard and any future changes
    to urlparse module should conform with it.  The urlparse module is
    currently not entirely compliant with this RFC due to defacto
    scenarios for parsing, and for backward compatibility purposes,
    some parsing quirks from older RFCs are retained.

This module aims to provide fully RFC 3986 compliant replacements for
the most commonly used functions found in :mod:`urllib.parse`.  It
also includes functions for distinguishing between the different forms
of URIs and URI references, and for conveniently creating URIs from
their individual components.

.. seealso::

   :rfc:`3986` - Uniform Resource Identifier (URI): Generic Syntax
        The current Internet standard (STD66) defining URI syntax, to
        which any changes to :mod:`uritools` should conform.  If
        deviations are observed, the module's implementation should be
        changed, even if this means breaking backward compatibility.


URI Classification
==================

According to RFC 3986, a URI reference is either a URI or a *relative
reference*.  If the URI reference's prefix does not match the syntax
of a scheme followed by its colon separator, then the URI reference is
a relative reference.

A relative reference that begins with two slash characters is termed a
*network-path* reference.  A relative reference that begins with a
single slash character is termed an *absolute-path* reference.  A
relative reference that does not begin with a slash character is
termed a *relative-path* reference.

When a URI reference refers to a URI that is, aside from its fragment
component, identical to the base URI, that reference is called a
*same-document* reference.  Examples of same-document references are
relative references that are empty or include only the number sign
("#") separator followed by a fragment identifier.

A URI without a fragment identifier is termed an *absolute URI*.  A
base URI, for example, must be an absolute URI.  If the base URI is
obtained from a URI reference, then that reference must be stripped of
any fragment component prior to its use as a base URI.

.. autofunction:: isuri

.. autofunction:: isabsuri

.. autofunction:: isnetpath

.. autofunction:: isabspath

.. autofunction:: isrelpath

.. autofunction:: issamedoc


URI Composition
===============

.. autofunction:: uricompose

   All components may be specified as either Unicode strings, which
   will be encoded according to `encoding`, or :class:`bytes` objects.

   `authority` may also be passed a three-item iterable specifying
   userinfo, host and port subcomponents.  If both `authority` and any
   of the `userinfo`, `host` or `port` keyword arguments are given,
   the keyword argument will override the corresponding `authority`
   subcomponent.

   `query` may also be passed a mapping object or a sequence of
   two-element tuples, which will be converted to a string of
   `name=value` pairs separated by `querysep`.

   The returned URI reference is of type :class:`str`.

.. autofunction:: urijoin

    If `strict` is :const:`False`, a scheme in the reference is
    ignored if it is identical to the base URI's scheme.

.. autofunction:: uriunsplit


URI Decomposition
=================

.. autofunction:: uridefrag

   The return value is an instance of a subclass of
   :class:`collections.namedtuple` with the following read-only
   attributes:

   +-------------------+-------+---------------------------------------------+
   | Attribute         | Index | Value                                       |
   +===================+=======+=============================================+
   | :attr:`uri`       | 0     | Absolute URI, or relative reference without |
   |                   |       | a fragment identifier                       |
   +-------------------+-------+---------------------------------------------+
   | :attr:`fragment`  | 1     | Fragment identifier, or :const:`None` if no |
   |                   |       | fragment was present                        |
   +-------------------+-------+---------------------------------------------+

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
   | :attr:`userinfo`  |       | Userinfo subcomponent of `authority`,       |
   |                   |       | or :const:`None` if not present             |
   +-------------------+-------+---------------------------------------------+
   | :attr:`host`      |       | Host subcomponent of `authority`,           |
   |                   |       | or :const:`None` if not present             |
   +-------------------+-------+---------------------------------------------+
   | :attr:`port`      |       | Port subcomponent of `authority` as a       |
   |                   |       | (possibly empty) string,                    |
   |                   |       | or :const:`None` if not present             |
   +-------------------+-------+---------------------------------------------+


URI Encoding
============

.. autofunction:: uridecode

   If `encoding` is set to :const:`None`, return the percent-decoded
   `uristring` as a :class:`bytes` object.  Otherwise, replace any
   percent-encodings and decode `uristring` using the codec registered
   for `encoding`, returning a Unicode string.

.. autofunction:: uriencode

   If `uristring` is a :class:`bytes` object, replace any characters
   not in :const:`UNRESERVED` or `safe` with their corresponding
   percent-encodings and return the result as a :class:`bytes` object.
   Otherwise, encode `uristring` using the codec registered for
   `encoding` before replacing any percent encodings.


Structured Parse Results
========================

The result objects from the :func:`uridefrag` and :func:`urisplit`
functions are instances of subclasses of
:class:`collections.namedtuple`.  These objects contain the attributes
described in the function documentation, as well as some additional
convenience methods.

.. autoclass:: DefragResult
   :members:

.. autoclass:: SplitResult
   :members:


Character Constants
===================

.. data:: GEN_DELIMS

   A string containing all general delimiting characters specified in
   RFC 3986.

.. data:: RESERVED

   A string containing all reserved characters specified in RFC 3986.

.. data:: SUB_DELIMS

   A string containing all subcomponent delimiting characters
   specified in RFC 3986.

.. data:: UNRESERVED

   A string containing all unreserved characters specified in
   RFC 3986.
