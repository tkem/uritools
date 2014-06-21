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

    def test_querylist(self):
        self.check(
            b'foo://example.com:8042/over/there?name=ferret#nose',
            scheme=b'foo',
            authority=b'example.com:8042',
            path=b'/over/there',
            query=[(b'name', b'ferret')],
            fragment=b'nose'
        )
        self.check(
            u'foo://example.com:8042/over/there?name=ferret#nose',
            scheme=u'foo',
            authority=u'example.com:8042',
            path=u'/over/there',
            query=[(u'name', u'ferret')],
            fragment=u'nose'
        )
        self.check(
            b'foo://example.com:8042/over/there?name=ferret#nose',
            scheme=b'foo',
            authority=b'example.com:8042',
            path=b'/over/there',
            query=[b'name=ferret'],
            fragment=b'nose',
            querysep=None
        )
        self.check(
            u'foo://example.com:8042/over/there?name=ferret#nose',
            scheme=u'foo',
            authority=u'example.com:8042',
            path=u'/over/there',
            query=[u'name=ferret'],
            fragment=u'nose',
            querysep=None
        )
        self.check(
            b'foo://example.com:8042/over/there?name=swallow&type=African#beak',
            scheme=b'foo',
            authority=b'example.com:8042',
            path=b'/over/there',
            query=[(b'name', b'swallow'), (b'type', b'African')],
            fragment=b'beak'
        )
        self.check(
            u'foo://example.com:8042/over/there?name=swallow&type=African#beak',
            scheme=u'foo',
            authority=u'example.com:8042',
            path=u'/over/there',
            query=[(u'name', u'swallow'), (u'type', u'African')],
            fragment=u'beak'
        )


    def test_querydict(self):
        self.check(
            b'foo://example.com:8042/over/there?name=ferret#nose',
            scheme=b'foo',
            authority=b'example.com:8042',
            path=b'/over/there',
            query={b'name': b'ferret'},
            fragment=b'nose'
        )
        self.check(
            u'foo://example.com:8042/over/there?name=ferret#nose',
            scheme=u'foo',
            authority=u'example.com:8042',
            path=u'/over/there',
            query={u'name': u'ferret'},
            fragment=u'nose'
        )
