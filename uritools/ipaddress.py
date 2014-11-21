import re

# RFC 3986 3.2.2: A host identified by an IPv6 literal address is
# represented inside the square brackets without a preceding version
# flag.  The ABNF provided here is a translation of the text
# definition of an IPv6 literal address provided in [RFC3513].  This
# syntax does not support IPv6 scoped addressing zone identifiers.
#
# IPv6address =                            6( h16 ":" ) ls32
#             /                       "::" 5( h16 ":" ) ls32
#             / [               h16 ] "::" 4( h16 ":" ) ls32
#             / [ *1( h16 ":" ) h16 ] "::" 3( h16 ":" ) ls32
#             / [ *2( h16 ":" ) h16 ] "::" 2( h16 ":" ) ls32
#             / [ *3( h16 ":" ) h16 ] "::"    h16 ":"   ls32
#             / [ *4( h16 ":" ) h16 ] "::"              ls32
#             / [ *5( h16 ":" ) h16 ] "::"              h16
#             / [ *6( h16 ":" ) h16 ] "::"
#
# ls32        = ( h16 ":" h16 ) / IPv4address
#             ; least-significant 32 bits of address
#
# h16         = 1*4HEXDIG
#             ; 16 bits of address represented in hexadecimal
IPV6_ADDRESS_RE = re.compile(r"""
\A
(?:
  (?:
                                              (?:[0-9A-F]{1,4}:){6}
  |                                         ::(?:[0-9A-F]{1,4}:){5}
  | (?:                      [0-9A-F]{1,4})?::(?:[0-9A-F]{1,4}:){4}
  | (?:(?:[0-9A-F]{1,4}:){,1}[0-9A-F]{1,4})?::(?:[0-9A-F]{1,4}:){3}
  | (?:(?:[0-9A-F]{1,4}:){,2}[0-9A-F]{1,4})?::(?:[0-9A-F]{1,4}:){2}
  | (?:(?:[0-9A-F]{1,4}:){,3}[0-9A-F]{1,4})?::   [0-9A-F]{1,4}:
  | (?:(?:[0-9A-F]{1,4}:){,4}[0-9A-F]{1,4})?::
  )
  (?:
    [0-9A-F]{1,4}:[0-9A-F]{1,4}                            # h16 ":" h16
  | (?:(?:25[0-5]|(?:2[0-4]|1[0-9]|[1-9])?[0-9])\.?\b){4}  # IPv4address
  )
| (?:(?:[0-9A-F]{1,4}:){,5}[0-9A-F]{1,4})?::[0-9A-F]{1,4}
| (?:(?:[0-9A-F]{1,4}:){,6}[0-9A-F]{1,4})?::
)
\Z
""", flags=(re.IGNORECASE | re.VERBOSE))


def ip_address(address):
    # RFC 3986 3.2.2: In anticipation of future, as-yet-undefined IP
    # literal address formats, an implementation may use an optional
    # version flag to indicate such a format explicitly rather than
    # rely on heuristic determination.
    #
    #  IP-literal = "[" ( IPv6address / IPvFuture  ) "]"
    #
    #  IPvFuture  = "v" 1*HEXDIG "." 1*( unreserved / sub-delims / ":" )
    #
    # The version flag does not indicate the IP version; rather, it
    # indicates future versions of the literal format.  As such,
    # implementations must not provide the version flag for the
    # existing IPv4 and IPv6 literal address forms described below.
    # If a URI containing an IP-literal that starts with "v"
    # (case-insensitive), indicating that the version flag is present,
    # is dereferenced by an application that does not know the meaning
    # of that version flag, then the application should return an
    # appropriate error for "address mechanism not supported".
    if address.startswith('v'):
        raise ValueError('%r address mechanism not supported' % address)
    elif IPV6_ADDRESS_RE.match(address):
        return address.lower()
    else:
        raise ValueError('%r does not appear to be an IPv6 address' % address)
