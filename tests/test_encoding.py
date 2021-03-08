import unittest

from uritools import RESERVED, UNRESERVED, uridecode, uriencode


class EncodingTest(unittest.TestCase):
    def check(self, decoded, encoded, safe="", encoding="utf-8"):
        self.assertEqual(uriencode(decoded, safe, encoding), encoded)
        self.assertEqual(uridecode(encoded, encoding), decoded)
        # swap bytes/string types
        self.assertEqual(
            uriencode(decoded.encode(encoding), safe, encoding), encoded
        )  # noqa
        self.assertEqual(uridecode(encoded.decode("ascii"), encoding), decoded)

    def test_encoding(self):
        cases = [
            ("", b""),
            (" ", b"%20"),
            ("%", b"%25"),
            ("~", b"~"),
            (UNRESERVED, UNRESERVED.encode("ascii")),
        ]
        for decoded, encoded in cases:
            self.check(decoded, encoded)

    def test_safe_encoding(self):
        cases = [
            ("", b"", ""),
            ("", b"", b""),
            (" ", b" ", " "),
            (" ", b" ", b" "),
            ("%", b"%", "%"),
            ("%", b"%", b"%"),
            (RESERVED, RESERVED.encode("ascii"), RESERVED),
        ]
        for decoded, encoded, safe in cases:
            self.check(decoded, encoded, safe)

    def test_utf8_encoding(self):
        cases = [("\xf6lk\xfcrbis", b"%C3%B6lk%C3%BCrbis")]
        for decoded, encoded in cases:
            self.check(decoded, encoded, encoding="utf-8")

    def test_latin1_encoding(self):
        cases = [("\xf6lk\xfcrbis", b"%F6lk%FCrbis")]
        for decoded, encoded in cases:
            self.check(decoded, encoded, encoding="latin-1")

    def test_idna_encoding(self):
        cases = [("\xf6lk\xfcrbis", b"xn--lkrbis-vxa4c")]
        for decoded, encoded in cases:
            self.check(decoded, encoded, encoding="idna")

    def test_decode_bytes(self):
        cases = [
            ("%F6lk%FCrbis", b"\xf6lk\xfcrbis"),
            (b"%F6lk%FCrbis", b"\xf6lk\xfcrbis"),
        ]
        for input, output in cases:
            self.assertEqual(uridecode(input, encoding=None), output)

    def test_encode_bytes(self):
        cases = [(b"\xf6lk\xfcrbis", b"%F6lk%FCrbis")]
        for input, output in cases:
            self.assertEqual(uriencode(input, encoding=None), output)

    def test_decode_errors(self):
        cases = [
            (UnicodeError, b"%FF", "utf-8"),
        ]
        for exception, string, encoding in cases:
            self.assertRaises(exception, uridecode, string, encoding)

    def test_encode_errors(self):
        cases = [
            (UnicodeError, "\xff", b"", "ascii"),
        ]
        for exception, string, safe, encoding in cases:
            self.assertRaises(exception, uriencode, string, safe, encoding)
