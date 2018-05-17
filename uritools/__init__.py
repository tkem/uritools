"""RFC 3986 compliant, Unicode-aware, scheme-agnostic replacement for
urlparse.

This module defines RFC 3986 compliant replacements for the most
commonly used functions of the Python 2.7 Standard Library
:mod:`urlparse` module.

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
    'isuri',
    'isabsuri',
    'isnetpath',
    'isabspath',
    'isrelpath',
    'issamedoc',
    'uricompose',
    'uridecode',
    'uridefrag',
    'uriencode',
    'urijoin',
    'urisplit',
    'uriunsplit'
)

__version__ = '2.2.0'
