from __future__ import unicode_literals

import unittest

from uritools import uricompose


class UricomposeTest(unittest.TestCase):

    def test_rfc3986(self):
        self.assertEqual(
            uricompose(
                scheme='foo',
                authority='example.com:8042',
                path='/over/there',
                query='name=ferret',
                fragment='nose'
            ),
            'foo://example.com:8042/over/there?name=ferret#nose'
        )
        self.assertEqual(
            uricompose(scheme='urn', path='example:animal:ferret:nose'),
            'urn:example:animal:ferret:nose'
        )
