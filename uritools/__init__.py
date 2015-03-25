"""RFC 3986 compliant, Unicode-aware, scheme-agnostic replacement for
urlparse.

This module defines RFC 3986 compliant replacements for the most
commonly used functions of the Python 2.7 Standard Library
:mod:`urlparse` module.

"""

from .const import GEN_DELIMS, SUB_DELIMS, RESERVED, UNRESERVED
from .parse import SplitResult, urisplit, uriunsplit, urijoin
from .defrag import DefragResult, uridefrag
from .encoding import uriencode, uridecode
from .compose import uricompose

__all__ = (
    'GEN_DELIMS', 'SUB_DELIMS', 'RESERVED', 'UNRESERVED',
    'SplitResult', 'urisplit', 'uriunsplit', 'urijoin',
    'DefragResult', 'uridefrag',
    'uriencode', 'uridecode',
    'uricompose'
)

__version__ = '0.11.1'
