import unittest

from uritools import uriunsplit


class UnsplitTest(unittest.TestCase):
    def check(self, split, uri):
        result = uriunsplit(split)
        self.assertEqual(result, uri)

    def test_rfc3986_3(self):
        """uriunsplit test cases from [RFC3986] 3. Syntax Components"""
        cases = [
            (
                ("foo", "example.com:8042", "/over/there", "name=ferret", "nose"),
                "foo://example.com:8042/over/there?name=ferret#nose",
            ),
            (
                ("urn", None, "example:animal:ferret:nose", None, None),
                "urn:example:animal:ferret:nose",
            ),
            (
                (b"foo", b"example.com:8042", b"/over/there", b"name=ferret", b"nose"),
                b"foo://example.com:8042/over/there?name=ferret#nose",
            ),
            (
                (b"urn", None, b"example:animal:ferret:nose", None, None),
                b"urn:example:animal:ferret:nose",
            ),
        ]
        for uri, parts in cases:
            self.check(uri, parts)
