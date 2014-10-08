import re

RE = re.compile(r"""
(?:(?P<scheme>[^:/?#]+):)?      # scheme
(?://(?P<authority>[^/?#]*))?   # authority
(?P<path>[^?#]*)                # path
(?:\?(?P<query>[^#]*))?         # query
(?:\#(?P<fragment>.*))?         # fragment
""", flags=re.VERBOSE)
"""Regular expression for splitting a well-formed URI into its
components, as specified in RFC 3986 Appendix B.

"""

# RFC 3986 3.2: scheme = ALPHA *( ALPHA / DIGIT / "+" / "-" / "." )
_SCHEME_RE = re.compile(r"\A[A-Z][A-Z0-9+.-]*\Z", flags=re.IGNORECASE)

# RFC 3986 3.2: authority = [ userinfo "@" ] host [ ":" port ]
_AUTHORITY_RE = re.compile(r"""
\A
(?:(.*)@)?      # userinfo
(.*?)           # host
(?::(\d*))?     # port
\Z
""", flags=re.VERBOSE)

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
_IPV6_ADDRESS_RE = re.compile(r"""
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
