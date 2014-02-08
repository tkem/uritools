from __future__ import unicode_literals

import unittest

from uritools import urisplit


class UrisplitTest(unittest.TestCase):

    def test_rfc3986(self):
        self.assertEqual(
            urisplit('foo://example.com:8042/over/there?name=ferret#nose'),
            ('foo', 'example.com:8042', '/over/there', 'name=ferret', 'nose')
        )
        self.assertEqual(
            urisplit('urn:example:animal:ferret:nose'),
            ('urn', None, 'example:animal:ferret:nose', None, None)
        )
