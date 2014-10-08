GEN_DELIMS = ':/?#[]@'
"""General delimiting characters as specified in RFC 3986."""

SUB_DELIMS = "!$&'()*+,;="
"""Subcomponent delimiting characters as specified in RFC 3986."""

RESERVED = GEN_DELIMS + SUB_DELIMS
"""Reserved characters as specified in RFC 3986."""

UNRESERVED = (
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    'abcdefghijklmnopqrstuvwxyz'
    '0123456789'
    '_.-~'
)
"""Unreserved characters as specified in RFC 3986."""
