"""RFC 3986 compliant, Unicode-aware, scheme-agnostic replacement for
urlparse.

This module defines RFC 3986 compliant replacements for the most
commonly used functions of the Python 2.7 Standard Library
:mod:`urlparse` module.

"""

from .compose import uricompose
from .const import GEN_DELIMS, RESERVED, SUB_DELIMS, UNRESERVED
from .defrag import DefragResult, uridefrag
from .encoding import uridecode, uriencode
from .parse import SplitResult, urijoin, urisplit, uriunsplit

__all__ = (
    'GEN_DELIMS', 'SUB_DELIMS', 'RESERVED', 'UNRESERVED',
    'SplitResult', 'urisplit', 'uriunsplit', 'urijoin',
    'DefragResult', 'uridefrag',
    'uriencode', 'uridecode',
    'uricompose'
)

__version__ = '0.11.1'
