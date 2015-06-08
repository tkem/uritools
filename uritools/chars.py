# RFC 3986 2.2.  Reserved Characters
#
#   reserved    = gen-delims / sub-delims
#
#   gen-delims  = ":" / "/" / "?" / "#" / "[" / "]" / "@"
#
#   sub-delims  = "!" / "$" / "&" / "'" / "(" / ")"
#               / "*" / "+" / "," / ";" / "="
#
GEN_DELIMS = ':/?#[]@'
SUB_DELIMS = "!$&'()*+,;="
RESERVED = GEN_DELIMS + SUB_DELIMS

# RFC 3986 2.3.  Unreserved Characters
#
#   unreserved  = ALPHA / DIGIT / "-" / "." / "_" / "~"
#
UNRESERVED = (
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    'abcdefghijklmnopqrstuvwxyz'
    '0123456789'
    '-._~'
)
