import unittest

from uritools import uridefrag


class UriJoinTest(unittest.TestCase):

    RFC3986_BASE = "http://a/b/c/d;p?q"

    def check(self, uri, base, fragment):
        result = uridefrag(uri)

        self.assertEqual(result, (base, fragment))
        self.assertEqual(result.base, base)
        self.assertEqual(result.fragment, fragment)

        self.assertEqual(result.getbase(), base)
        self.assertEqual(result.getfragment(), fragment)
        self.assertEqual(result.geturi(), uri)

    def test_uridefrag(self):
        for uri, base, fragment in [
            ('http://a/b/c/d;p?q', 'http://a/b/c/d;p?q', None),
            ('http://a/b/c/d;p?q#f', 'http://a/b/c/d;p?q', 'f'),
        ]:
            self.check(uri, base, fragment)
