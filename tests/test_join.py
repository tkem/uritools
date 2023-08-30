import unittest

from uritools import urijoin


class JoinTest(unittest.TestCase):
    RFC3986_BASE = "http://a/b/c/d;p?q"

    def check(self, base, ref, expected, strict=False):
        self.assertEqual(expected, urijoin(base, ref, strict))
        # base as bytes, ref as str
        self.assertEqual(expected, urijoin(base.encode(), ref, strict))
        # base as str, ref as bytes
        self.assertEqual(expected, urijoin(base, ref.encode(), strict))
        # both base and ref as bytes
        self.assertEqual(
            expected.encode(), urijoin(base.encode(), ref.encode(), strict)
        )

    def test_rfc3986_normal(self):
        """urijoin test cases from RFC 3986 5.4.1. Normal Examples"""
        self.check(self.RFC3986_BASE, "g:h", "g:h")
        self.check(self.RFC3986_BASE, "g", "http://a/b/c/g")
        self.check(self.RFC3986_BASE, "./g", "http://a/b/c/g")
        self.check(self.RFC3986_BASE, "g/", "http://a/b/c/g/")
        self.check(self.RFC3986_BASE, "/g", "http://a/g")
        self.check(self.RFC3986_BASE, "//g", "http://g")
        self.check(self.RFC3986_BASE, "?y", "http://a/b/c/d;p?y")
        self.check(self.RFC3986_BASE, "g?y", "http://a/b/c/g?y")
        self.check(self.RFC3986_BASE, "#s", "http://a/b/c/d;p?q#s")
        self.check(self.RFC3986_BASE, "g#s", "http://a/b/c/g#s")
        self.check(self.RFC3986_BASE, "g?y#s", "http://a/b/c/g?y#s")
        self.check(self.RFC3986_BASE, ";x", "http://a/b/c/;x")
        self.check(self.RFC3986_BASE, "g;x", "http://a/b/c/g;x")
        self.check(self.RFC3986_BASE, "g;x?y#s", "http://a/b/c/g;x?y#s")
        self.check(self.RFC3986_BASE, "", "http://a/b/c/d;p?q")
        self.check(self.RFC3986_BASE, ".", "http://a/b/c/")
        self.check(self.RFC3986_BASE, "./", "http://a/b/c/")
        self.check(self.RFC3986_BASE, "..", "http://a/b/")
        self.check(self.RFC3986_BASE, "../", "http://a/b/")
        self.check(self.RFC3986_BASE, "../g", "http://a/b/g")
        self.check(self.RFC3986_BASE, "../..", "http://a/")
        self.check(self.RFC3986_BASE, "../../", "http://a/")
        self.check(self.RFC3986_BASE, "../../g", "http://a/g")

    def test_rfc3986_abnormal(self):
        """urijoin test cases from RFC 3986 5.4.2. Abnormal Examples"""
        self.check(self.RFC3986_BASE, "../../../g", "http://a/g")
        self.check(self.RFC3986_BASE, "../../../../g", "http://a/g")
        self.check(self.RFC3986_BASE, "/./g", "http://a/g")
        self.check(self.RFC3986_BASE, "/../g", "http://a/g")
        self.check(self.RFC3986_BASE, "g.", "http://a/b/c/g.")
        self.check(self.RFC3986_BASE, ".g", "http://a/b/c/.g")
        self.check(self.RFC3986_BASE, "g..", "http://a/b/c/g..")
        self.check(self.RFC3986_BASE, "..g", "http://a/b/c/..g")
        self.check(self.RFC3986_BASE, "./../g", "http://a/b/g")
        self.check(self.RFC3986_BASE, "./g/.", "http://a/b/c/g/")
        self.check(self.RFC3986_BASE, "g/./h", "http://a/b/c/g/h")
        self.check(self.RFC3986_BASE, "g/../h", "http://a/b/c/h")
        self.check(self.RFC3986_BASE, "g;x=1/./y", "http://a/b/c/g;x=1/y")
        self.check(self.RFC3986_BASE, "g;x=1/../y", "http://a/b/c/y")
        self.check(self.RFC3986_BASE, "g?y/./x", "http://a/b/c/g?y/./x")
        self.check(self.RFC3986_BASE, "g?y/../x", "http://a/b/c/g?y/../x")
        self.check(self.RFC3986_BASE, "g#s/./x", "http://a/b/c/g#s/./x")
        self.check(self.RFC3986_BASE, "g#s/../x", "http://a/b/c/g#s/../x")
        self.check(self.RFC3986_BASE, "http:g", "http:g", True)
        self.check(self.RFC3986_BASE, "http:g", "http://a/b/c/g", False)

    def test_rfc3986_merge(self):
        """urijoin test cases for RFC 3986 5.2.3. Merge Paths"""
        self.check("http://a", "b", "http://a/b")

    def test_relative_base(self):
        self.check("", "bar", "bar")
        self.check("foo", "bar", "bar")
        self.check("foo/", "bar", "foo/bar")
        self.check(".", "bar", "bar")
        self.check("./", "bar", "bar")
        self.check("./foo", "bar", "bar")
        self.check("./foo/", "bar", "foo/bar")
        self.check("..", "bar", "bar")
        self.check("../", "bar", "../bar")
        self.check("../foo", "bar", "../bar")
        self.check("../foo/", "bar", "../foo/bar")

        self.check("", "../bar", "../bar")
        self.check("foo", "../bar", "../bar")
        self.check("foo/", "../bar", "bar")
        self.check(".", "../bar", "../bar")
        self.check("./", "../bar", "../bar")
        self.check("./foo", "../bar", "../bar")
        self.check("./foo/", "../bar", "bar")
        self.check("..", "../bar", "../bar")
        self.check("../", "../bar", "../../bar")
        self.check("../foo", "../bar", "../../bar")
        self.check("../foo/", "../bar", "../bar")
