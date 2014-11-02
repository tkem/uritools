# RFC 3986 2.2: gen-delims = ":" / "/" / "?" / "#" / "[" / "]" / "@"
GEN_DELIMS = b':/?#[]@'

# RFC 3986 2.2: sub-delims = "!" / "$" / "&" / "'" / "(" / ")"
#                          / "*" / "+" / "," / ";" / "="
SUB_DELIMS = b"!$&'()*+,;="

# RFC 3986 2.2: reserved = gen-delims / sub-delims
RESERVED = GEN_DELIMS + SUB_DELIMS

# RFC 3986 2.3: unreserved = ALPHA / DIGIT / "-" / "." / "_" / "~"
UNRESERVED = (
    b'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    b'abcdefghijklmnopqrstuvwxyz'
    b'0123456789'
    b'_.-~'
)
