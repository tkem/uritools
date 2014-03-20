import unittest

from uritools import uricompose


class UriComposeTest(unittest.TestCase):

    def check(self, expected, **kwargs):
        result = uricompose(**kwargs)
        self.assertEqual(
            result, expected,
            '%r -> %r != %r' % (kwargs, result, expected)
        )

    def test_rfc3986(self):
        """uricompose test cases from [RFC3986] 3. Syntax Components"""
        self.check(
            b'foo://example.com:8042/over/there?name=ferret#nose',
            scheme=b'foo',
            authority=b'example.com:8042',
            path=b'/over/there',
            query=b'name=ferret',
            fragment=b'nose'
        )
        self.check(
            u'foo://example.com:8042/over/there?name=ferret#nose',
            scheme=u'foo',
            authority=u'example.com:8042',
            path=u'/over/there',
            query=u'name=ferret',
            fragment=u'nose'
        )
        self.check(
            b'urn:example:animal:ferret:nose',
            scheme=b'urn',
            path=b'example:animal:ferret:nose'
        )
        self.check(
            u'urn:example:animal:ferret:nose',
            scheme=u'urn',
            path=u'example:animal:ferret:nose'
        )
