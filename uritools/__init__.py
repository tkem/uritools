"""RFC 3986 compliant, scheme-agnostic replacement for `urllib.parse`.

This module defines RFC 3986 compliant replacements for the most
commonly used functions of the Python Standard Library
:mod:`urllib.parse` module.

"""

from .chars import GEN_DELIMS, RESERVED, SUB_DELIMS, UNRESERVED
from .classify import isabspath, isabsuri, isnetpath, isrelpath
from .classify import issamedoc, isuri
from .compose import uricompose
from .defrag import DefragResult, uridefrag
from .encoding import uridecode, uriencode
from .join import urijoin
from .split import SplitResult, urisplit, uriunsplit

__all__ = (
    'GEN_DELIMS',
    'RESERVED',
    'SUB_DELIMS',
    'UNRESERVED',
    'DefragResult',
    'SplitResult',
    'isabspath',
    'isabsuri',
    'isnetpath',
    'isrelpath',
    'issamedoc',
    'isuri',
    'uricompose',
    'uridecode',
    'uridefrag',
    'uriencode',
    'urijoin',
    'urisplit',
    'uriunsplit'
)

__version__ = '3.0.0'
