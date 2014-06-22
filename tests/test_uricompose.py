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
            'foo://example.com:8042/over/there?name=ferret#nose',
            scheme='foo',
            authority='example.com:8042',
            path='/over/there',
            query='name=ferret',
            fragment='nose'
        )
        self.check(
            'urn:example:animal:ferret:nose',
            scheme='urn',
            path='example:animal:ferret:nose'
        )

    def test_querylist(self):
        # FIXME: empty query?
        self.check(
            'foo://example.com:8042/over/there?#nose',
            scheme='foo',
            authority='example.com:8042',
            path='/over/there',
            query=[],
            fragment='nose'
        )
        self.check(
            'foo://example.com:8042/over/there?name=ferret#nose',
            scheme='foo',
            authority='example.com:8042',
            path='/over/there',
            query=[('name', 'ferret')],
            fragment='nose'
        )
        self.check(
            'foo://example.com:8042/over/there?name=ferret#nose',
            scheme='foo',
            authority='example.com:8042',
            path='/over/there',
            query=['name=ferret'],
            fragment='nose',
            querysep=None
        )
        self.check(
            'foo://example.com:8042/over/there?name=swallow&type=African#beak',
            scheme='foo',
            authority='example.com:8042',
            path='/over/there',
            query=[('name', 'swallow'), ('type', 'African')],
            fragment='beak'
        )

    def test_querydict(self):
        # FIXME: empty query?
        self.check(
            'foo://example.com:8042/over/there?#nose',
            scheme='foo',
            authority='example.com:8042',
            path='/over/there',
            query={},
            fragment='nose'
        )
        self.check(
            'foo://example.com:8042/over/there?name=ferret#nose',
            scheme='foo',
            authority='example.com:8042',
            path='/over/there',
            query={'name': 'ferret'},
            fragment='nose'
        )
