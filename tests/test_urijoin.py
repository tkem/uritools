import unittest

from uritools import urijoin

RFC1808_BASE = "http://a/b/c/d;p?q#f"
RFC2396_BASE = "http://a/b/c/d;p?q"
RFC3986_BASE = "http://a/b/c/d;p?q"


class UriJoinTest(unittest.TestCase):

    def check(self, base, ref, expected, strict=False):
        result = urijoin(base, ref, strict)
        self.assertEqual(
            result, expected,
            '(%r, %r) -> %r != %r' % (base, ref, result, expected)
        )

    def test_rfc3986_5_4_1(self):
        """urijoin test cases from RFC 3986 5.4.1. Normal Examples"""

        self.check(RFC3986_BASE, "g:h", "g:h")
        self.check(RFC3986_BASE, "g", "http://a/b/c/g")
        self.check(RFC3986_BASE, "./g", "http://a/b/c/g")
        self.check(RFC3986_BASE, "g/", "http://a/b/c/g/")
        self.check(RFC3986_BASE, "/g", "http://a/g")
        self.check(RFC3986_BASE, "//g", "http://g")
        self.check(RFC3986_BASE, "?y", "http://a/b/c/d;p?y")
        self.check(RFC3986_BASE, "g?y", "http://a/b/c/g?y")
        self.check(RFC3986_BASE, "#s", "http://a/b/c/d;p?q#s")
        self.check(RFC3986_BASE, "g#s", "http://a/b/c/g#s")
        self.check(RFC3986_BASE, "g?y#s", "http://a/b/c/g?y#s")
        self.check(RFC3986_BASE, ";x", "http://a/b/c/;x")
        self.check(RFC3986_BASE, "g;x", "http://a/b/c/g;x")
        self.check(RFC3986_BASE, "g;x?y#s", "http://a/b/c/g;x?y#s")
        self.check(RFC3986_BASE, "", "http://a/b/c/d;p?q")
        self.check(RFC3986_BASE, ".", "http://a/b/c/")
        self.check(RFC3986_BASE, "./", "http://a/b/c/")
        self.check(RFC3986_BASE, "..", "http://a/b/")
        self.check(RFC3986_BASE, "../", "http://a/b/")
        self.check(RFC3986_BASE, "../g", "http://a/b/g")
        self.check(RFC3986_BASE, "../..", "http://a/")
        self.check(RFC3986_BASE, "../../", "http://a/")
        self.check(RFC3986_BASE, "../../g", "http://a/g")

    def test_rfc3986_5_4_2(self):
        """urijoin test cases from RFC 3986 5.4.2. Abnormal Examples"""

        self.check(RFC3986_BASE, "../../../g", "http://a/g")
        self.check(RFC3986_BASE, "../../../../g", "http://a/g")

        self.check(RFC3986_BASE, "/./g", "http://a/g")
        self.check(RFC3986_BASE, "/../g", "http://a/g")
        self.check(RFC3986_BASE, "g.", "http://a/b/c/g.")
        self.check(RFC3986_BASE, ".g", "http://a/b/c/.g")
        self.check(RFC3986_BASE, "g..", "http://a/b/c/g..")
        self.check(RFC3986_BASE, "..g", "http://a/b/c/..g")

        self.check(RFC3986_BASE, "./../g", "http://a/b/g")
        self.check(RFC3986_BASE, "./g/.", "http://a/b/c/g/")
        self.check(RFC3986_BASE, "g/./h", "http://a/b/c/g/h")
        self.check(RFC3986_BASE, "g/../h", "http://a/b/c/h")
        self.check(RFC3986_BASE, "g;x=1/./y", "http://a/b/c/g;x=1/y")
        self.check(RFC3986_BASE, "g;x=1/../y", "http://a/b/c/y")

        self.check(RFC3986_BASE, "g?y/./x", "http://a/b/c/g?y/./x")
        self.check(RFC3986_BASE, "g?y/../x", "http://a/b/c/g?y/../x")
        self.check(RFC3986_BASE, "g#s/./x", "http://a/b/c/g#s/./x")
        self.check(RFC3986_BASE, "g#s/../x", "http://a/b/c/g#s/../x")

        self.check(RFC3986_BASE, "http:g", "http:g", True)
        self.check(RFC3986_BASE, "http:g", "http://a/b/c/g", False)

    def test_urlparse_RFC1808(self):
        """urlparse.urljoin test cases from RFC 1808"""

        # "normal" cases from RFC 1808:
        self.check(RFC1808_BASE, 'g:h', 'g:h')
        self.check(RFC1808_BASE, 'g', 'http://a/b/c/g')
        self.check(RFC1808_BASE, './g', 'http://a/b/c/g')
        self.check(RFC1808_BASE, 'g/', 'http://a/b/c/g/')
        self.check(RFC1808_BASE, '/g', 'http://a/g')
        self.check(RFC1808_BASE, '//g', 'http://g')
        self.check(RFC1808_BASE, 'g?y', 'http://a/b/c/g?y')
        self.check(RFC1808_BASE, 'g?y/./x', 'http://a/b/c/g?y/./x')
        self.check(RFC1808_BASE, '#s', 'http://a/b/c/d;p?q#s')
        self.check(RFC1808_BASE, 'g#s', 'http://a/b/c/g#s')
        self.check(RFC1808_BASE, 'g#s/./x', 'http://a/b/c/g#s/./x')
        self.check(RFC1808_BASE, 'g?y#s', 'http://a/b/c/g?y#s')
        self.check(RFC1808_BASE, 'g;x', 'http://a/b/c/g;x')
        self.check(RFC1808_BASE, 'g;x?y#s', 'http://a/b/c/g;x?y#s')
        self.check(RFC1808_BASE, '.', 'http://a/b/c/')
        self.check(RFC1808_BASE, './', 'http://a/b/c/')
        self.check(RFC1808_BASE, '..', 'http://a/b/')
        self.check(RFC1808_BASE, '../', 'http://a/b/')
        self.check(RFC1808_BASE, '../g', 'http://a/b/g')
        self.check(RFC1808_BASE, '../..', 'http://a/')
        self.check(RFC1808_BASE, '../../', 'http://a/')
        self.check(RFC1808_BASE, '../../g', 'http://a/g')

        # "abnormal" cases from RFC 1808:
        #self.check(RFC1808_BASE, '', 'http://a/b/c/d;p?q#f')
        #self.check(RFC1808_BASE, '../../../g', 'http://a/../g')
        #self.check(RFC1808_BASE, '../../../../g', 'http://a/../../g')
        #self.check(RFC1808_BASE, '/./g', 'http://a/./g')
        #self.check(RFC1808_BASE, '/../g', 'http://a/../g')
        self.check(RFC1808_BASE, 'g.', 'http://a/b/c/g.')
        self.check(RFC1808_BASE, '.g', 'http://a/b/c/.g')
        self.check(RFC1808_BASE, 'g..', 'http://a/b/c/g..')
        self.check(RFC1808_BASE, '..g', 'http://a/b/c/..g')
        self.check(RFC1808_BASE, './../g', 'http://a/b/g')
        self.check(RFC1808_BASE, './g/.', 'http://a/b/c/g/')
        self.check(RFC1808_BASE, 'g/./h', 'http://a/b/c/g/h')
        self.check(RFC1808_BASE, 'g/../h', 'http://a/b/c/h')

        # RFC 1808 and RFC 1630 disagree on these (according to RFC 1808),
        # so we'll not actually run these tests (which expect 1808 behavior).
        self.check(RFC1808_BASE, 'http:g', 'http:g', True)
        self.check(RFC1808_BASE, 'http:', 'http:', True)

    def test_urlparse_RFC2396(self):
        """urlparse.urljoin test cases from RFC 2396"""

        self.check(RFC2396_BASE, 'g:h', 'g:h')
        self.check(RFC2396_BASE, 'g', 'http://a/b/c/g')
        self.check(RFC2396_BASE, './g', 'http://a/b/c/g')
        self.check(RFC2396_BASE, 'g/', 'http://a/b/c/g/')
        self.check(RFC2396_BASE, '/g', 'http://a/g')
        self.check(RFC2396_BASE, '//g', 'http://g')
        self.check(RFC2396_BASE, 'g?y', 'http://a/b/c/g?y')
        self.check(RFC2396_BASE, '#s', 'http://a/b/c/d;p?q#s')
        self.check(RFC2396_BASE, 'g#s', 'http://a/b/c/g#s')
        self.check(RFC2396_BASE, 'g?y#s', 'http://a/b/c/g?y#s')
        self.check(RFC2396_BASE, 'g;x', 'http://a/b/c/g;x')
        self.check(RFC2396_BASE, 'g;x?y#s', 'http://a/b/c/g;x?y#s')
        self.check(RFC2396_BASE, '.', 'http://a/b/c/')
        self.check(RFC2396_BASE, './', 'http://a/b/c/')
        self.check(RFC2396_BASE, '..', 'http://a/b/')
        self.check(RFC2396_BASE, '../', 'http://a/b/')
        self.check(RFC2396_BASE, '../g', 'http://a/b/g')
        self.check(RFC2396_BASE, '../..', 'http://a/')
        self.check(RFC2396_BASE, '../../', 'http://a/')
        self.check(RFC2396_BASE, '../../g', 'http://a/g')
        self.check(RFC2396_BASE, '', RFC2396_BASE)
        #self.check(RFC2396_BASE, '../../../g', 'http://a/../g')
        #self.check(RFC2396_BASE, '../../../../g', 'http://a/../../g')
        #self.check(RFC2396_BASE, '/./g', 'http://a/./g')
        #self.check(RFC2396_BASE, '/../g', 'http://a/../g')
        self.check(RFC2396_BASE, 'g.', 'http://a/b/c/g.')
        self.check(RFC2396_BASE, '.g', 'http://a/b/c/.g')
        self.check(RFC2396_BASE, 'g..', 'http://a/b/c/g..')
        self.check(RFC2396_BASE, '..g', 'http://a/b/c/..g')
        self.check(RFC2396_BASE, './../g', 'http://a/b/g')
        self.check(RFC2396_BASE, './g/.', 'http://a/b/c/g/')
        self.check(RFC2396_BASE, 'g/./h', 'http://a/b/c/g/h')
        self.check(RFC2396_BASE, 'g/../h', 'http://a/b/c/h')
        self.check(RFC2396_BASE, 'g;x=1/./y', 'http://a/b/c/g;x=1/y')
        self.check(RFC2396_BASE, 'g;x=1/../y', 'http://a/b/c/y')
        self.check(RFC2396_BASE, 'g?y/./x', 'http://a/b/c/g?y/./x')
        self.check(RFC2396_BASE, 'g?y/../x', 'http://a/b/c/g?y/../x')
        self.check(RFC2396_BASE, 'g#s/./x', 'http://a/b/c/g#s/./x')
        self.check(RFC2396_BASE, 'g#s/../x', 'http://a/b/c/g#s/../x')
