import unittest

from uritools import uriunsplit


class UriUnsplitTest(unittest.TestCase):

    def check(self, split, uri):
        result = uriunsplit(split)
        self.assertEqual(result, uri)

    def test_rfc3986_3(self):
        """uriunsplit test cases from [RFC3986] 3. Syntax Components"""

        self.check(
            ('foo', 'example.com:8042', '/over/there', 'name=ferret', 'nose'),
            'foo://example.com:8042/over/there?name=ferret#nose'
        )
        self.check(
            ('urn', None, 'example:animal:ferret:nose', None, None),
            'urn:example:animal:ferret:nose'
        )
