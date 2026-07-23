import unittest

from uritools import uridefrag


class DefragTest(unittest.TestCase):
    def test_uridefrag(self):
        cases = [
            ("http://python.org#frag", "http://python.org", "frag"),
            ("http://python.org", "http://python.org", None),
            ("http://python.org/#frag", "http://python.org/", "frag"),
            ("http://python.org/", "http://python.org/", None),
            ("http://python.org/?q#frag", "http://python.org/?q", "frag"),
            ("http://python.org/?q", "http://python.org/?q", None),
            ("http://python.org/p#frag", "http://python.org/p", "frag"),
            ("http://python.org/p?q", "http://python.org/p?q", None),
            ("http://python.org#", "http://python.org", ""),
            ("http://python.org/#", "http://python.org/", ""),
            ("http://python.org/?q#", "http://python.org/?q", ""),
            ("http://python.org/p?q#", "http://python.org/p?q", ""),
        ]

        def encode(s):
            return s.encode() if s is not None else None

        cases += [map(encode, case) for case in cases]

        for uri, base, fragment in cases:
            defrag = uridefrag(uri)
            self.assertEqual(defrag, (base, fragment))
            self.assertEqual(defrag.uri, base)
            self.assertEqual(defrag.fragment, fragment)
            self.assertEqual(uri, defrag.geturi())

    def test_getfragment(self):
        self.assertEqual(uridefrag("").getfragment(), None)
        self.assertEqual(uridefrag(b"").getfragment(), None)
        self.assertEqual(uridefrag("#").getfragment(), "")
        self.assertEqual(uridefrag(b"#").getfragment(), "")
        self.assertEqual(uridefrag("#foo").getfragment(), "foo")
        self.assertEqual(uridefrag(b"#foo").getfragment(), "foo")
        self.assertEqual(uridefrag("#foo%20bar").getfragment(), "foo bar")
        self.assertEqual(uridefrag(b"#foo%20bar").getfragment(), "foo bar")

    def test_getfragment_encoding_none(self):
        self.assertEqual(uridefrag("").getfragment(encoding=None), None)
        self.assertEqual(uridefrag(b"").getfragment(encoding=None), None)
        self.assertEqual(uridefrag("#").getfragment(encoding=None), b"")
        self.assertEqual(uridefrag(b"#").getfragment(encoding=None), b"")
        self.assertEqual(uridefrag("#foo").getfragment(encoding=None), b"foo")
        self.assertEqual(uridefrag(b"#foo").getfragment(encoding=None), b"foo")
        self.assertEqual(uridefrag("#foo%20bar").getfragment(encoding=None), b"foo bar")
        self.assertEqual(
            uridefrag(b"#foo%20bar").getfragment(encoding=None), b"foo bar"
        )
