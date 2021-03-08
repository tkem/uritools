import unittest

import uritools


class ClassifyTest(unittest.TestCase):
    def test_classification(self):
        cases = [
            ("", False, False, False, False, True, True),
            ("#", False, False, False, False, True, True),
            ("#f", False, False, False, False, True, True),
            ("?", False, False, False, False, True, False),
            ("?q", False, False, False, False, True, False),
            ("p", False, False, False, False, True, False),
            ("/p", False, False, False, True, False, False),
            ("/p?", False, False, False, True, False, False),
            ("/p?q", False, False, False, True, False, False),
            ("/p#", False, False, False, True, False, False),
            ("/p#f", False, False, False, True, False, False),
            ("/p?q#f", False, False, False, True, False, False),
            ("//", False, False, True, False, False, False),
            ("//n?", False, False, True, False, False, False),
            ("//n?q", False, False, True, False, False, False),
            ("//n#", False, False, True, False, False, False),
            ("//n#f", False, False, True, False, False, False),
            ("//n?q#f", False, False, True, False, False, False),
            ("s:", True, True, False, False, False, False),
            ("s:p", True, True, False, False, False, False),
            ("s:p?", True, True, False, False, False, False),
            ("s:p?q", True, True, False, False, False, False),
            ("s:p#", True, False, False, False, False, False),
            ("s:p#f", True, False, False, False, False, False),
            ("s://", True, True, False, False, False, False),
            ("s://h", True, True, False, False, False, False),
            ("s://h/", True, True, False, False, False, False),
            ("s://h/p", True, True, False, False, False, False),
            ("s://h/p?", True, True, False, False, False, False),
            ("s://h/p?q", True, True, False, False, False, False),
            ("s://h/p#", True, False, False, False, False, False),
            ("s://h/p#f", True, False, False, False, False, False),
        ]
        for s, uri, absuri, netpath, abspath, relpath, samedoc in cases:
            for ref in [s, s.encode("ascii")]:
                parts = uritools.urisplit(ref)
                self.assertEqual(parts.isuri(), uri)
                self.assertEqual(parts.isabsuri(), absuri)
                self.assertEqual(parts.isnetpath(), netpath)
                self.assertEqual(parts.isabspath(), abspath)
                self.assertEqual(parts.isrelpath(), relpath)
                self.assertEqual(parts.issamedoc(), samedoc)
                self.assertEqual(uritools.isuri(ref), uri)
                self.assertEqual(uritools.isabsuri(ref), absuri)
                self.assertEqual(uritools.isnetpath(ref), netpath)
                self.assertEqual(uritools.isabspath(ref), abspath)
                self.assertEqual(uritools.isrelpath(ref), relpath)
                self.assertEqual(uritools.issamedoc(ref), samedoc)
