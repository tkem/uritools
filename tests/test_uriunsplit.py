from __future__ import unicode_literals

import unittest

from uritools import uriunsplit


class UriunsplitTest(unittest.TestCase):

    def test_rfc3986(self):
        self.assertEqual(
            uriunsplit([
                'foo', 'example.com:8042', '/over/there', 'name=ferret', 'nose'
            ]),
            'foo://example.com:8042/over/there?name=ferret#nose'
        )
        self.assertEqual(
            uriunsplit([
                'urn', None, 'example:animal:ferret:nose', None, None
            ]),
            'urn:example:animal:ferret:nose'
        )
