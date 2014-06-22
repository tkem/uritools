import unittest

from . import b, u
from uritools import uridefrag


class UriDefragTest(unittest.TestCase):

    RFC3986_BASE = "http://a/b/c/d;p?q"

    def check(self, uri, base, fragment):
        result = uridefrag(uri)

        self.assertEqual(result, (base, fragment))
        self.assertEqual(result.base, base)
        self.assertEqual(result.fragment, fragment)

        self.assertEqual(result.getbase(), u(base))
        self.assertEqual(result.getfragment(), u(fragment))
        self.assertEqual(result.geturi(), uri)

    def test_uridefrag(self):
        for uri, base, fragment in [
            (b('http://a/b/c/d;p?q'), b('http://a/b/c/d;p?q'), None),
            (b('http://a/b/c/d;p?q#f'), b('http://a/b/c/d;p?q'), b('f')),
            (u('http://a/b/c/d;p?q'), u('http://a/b/c/d;p?q'), None),
            (u('http://a/b/c/d;p?q#f'), u('http://a/b/c/d;p?q'), u('f')),
        ]:
            self.check(uri, base, fragment)
