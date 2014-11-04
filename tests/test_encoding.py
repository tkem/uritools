from __future__ import unicode_literals

import unittest

from uritools import uriencode, uridecode, RESERVED, UNRESERVED


class EncodingTest(unittest.TestCase):

    def check(self, decoded, encoded, safe=b'', encoding='utf-8'):
        self.assertEqual(uriencode(decoded, safe, encoding), encoded)
        self.assertEqual(uridecode(encoded, encoding), decoded)

        e = encoding
        self.assertEqual(uriencode(decoded.encode(e), safe, encoding), encoded)
        self.assertEqual(uridecode(encoded.decode('ascii'), encoding), decoded)

    def test_encoding(self):
        cases = [
            ('', b''),
            (' ', b'%20'),
            ('%', b'%25'),
            ('~', b'~'),
            (UNRESERVED.decode('ascii'), UNRESERVED),
        ]
        for decoded, encoded in cases:
            self.check(decoded, encoded)

    def test_safe_encoding(self):
        cases = [
            ('', b'', b''),
            (' ', b' ', b' '),
            ('%', b'%', b'%'),
            (RESERVED.decode('ascii'), RESERVED, RESERVED)
        ]
        for decoded, encoded, safe in cases:
            self.check(decoded, encoded, safe)

    def test_utf8_encoding(self):
        cases = [
            ('\xf6lk\xfcrbis', b'%C3%B6lk%C3%BCrbis')
        ]
        for decoded, encoded in cases:
            self.check(decoded, encoded, encoding='utf-8')

    def test_latin1_encoding(self):
        cases = [
            ('\xf6lk\xfcrbis', b'%F6lk%FCrbis')
        ]
        for decoded, encoded in cases:
            self.check(decoded, encoded, encoding='latin-1')

    def test_idna_encoding(self):
        cases = [
            ('\xf6lk\xfcrbis', b'xn--lkrbis-vxa4c')
        ]
        for decoded, encoded in cases:
            self.check(decoded, encoded, encoding='idna')
