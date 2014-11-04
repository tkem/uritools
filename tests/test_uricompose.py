import unittest

from uritools import uricompose, urisplit


class UriComposeTest(unittest.TestCase):

    def check(self, expected, **kwargs):
        uri = uricompose(**kwargs)
        self.assertEqual(
            expected, uri,
            '%r -> %r != %r' % (kwargs, uri, expected)
        )

    def test_rfc3986(self):
        """uricompose test cases from [RFC3986] 3. Syntax Components"""
        self.check(
            b'foo://example.com:8042/over/there?name=ferret#nose',
            scheme='foo',
            authority='example.com:8042',
            path='/over/there',
            query='name=ferret',
            fragment='nose'
        )
        self.check(
            b'urn:example:animal:ferret:nose',
            scheme='urn',
            path='example:animal:ferret:nose'
        )

    def test_querylist(self):
        self.check(
            b'foo://example.com:8042/over/there?#nose',
            scheme='foo',
            authority='example.com:8042',
            path='/over/there',
            query=[],
            fragment='nose'
        )
        self.check(
            b'foo://example.com:8042/over/there?name=ferret#nose',
            scheme='foo',
            authority='example.com:8042',
            path='/over/there',
            query=[('name', 'ferret')],
            fragment='nose'
        )
        self.check(
            b'foo://example.com:8042/over/there?id=42#nose',
            scheme='foo',
            authority='example.com:8042',
            path='/over/there',
            query=[('id', 42)],
            fragment='nose'
        )
        self.check(
            b'foo://example.com:8042/over/there?none#nose',
            scheme='foo',
            authority='example.com:8042',
            path='/over/there',
            query=[('none', None)],
            fragment='nose'
        )
        self.check(
            b'foo://example.com:8042/over/there?name=swallow&type=African#beak',  # noqa
            scheme='foo',
            authority='example.com:8042',
            path='/over/there',
            query=[('name', 'swallow'), ('type', 'African')],
            fragment='beak'
        )

    def test_querydict(self):
        self.check(
            b'foo://example.com:8042/over/there?#nose',
            scheme='foo',
            authority='example.com:8042',
            path='/over/there',
            query={},
            fragment='nose'
        )
        self.check(
            b'foo://example.com:8042/over/there?name=ferret#nose',
            scheme='foo',
            authority='example.com:8042',
            path='/over/there',
            query={'name': 'ferret'},
            fragment='nose'
        )
        self.check(
            b'foo://example.com:8042/over/there?id=42#nose',
            scheme='foo',
            authority='example.com:8042',
            path='/over/there',
            query={'id': 42},
            fragment='nose'
        )
        self.check(
            b'foo://example.com:8042/over/there?none#nose',
            scheme='foo',
            authority='example.com:8042',
            path='/over/there',
            query={'none': None},
            fragment='nose'
        )
        self.assertEqual(
            {'name': ['swallow'], 'type': ['African']},
            urisplit(uricompose(
                scheme='foo',
                authority='example.com:8042',
                path='/over/there',
                query={'name': 'swallow', 'type': 'African'},
                fragment='beak'
            )).getquerydict()
        )
        self.assertEqual(
            {'name': ['swallow'], 'type': ['African']},
            urisplit(uricompose(
                scheme='foo',
                authority='example.com:8042',
                path='/over/there',
                query={'name': ['swallow'], 'type': ['African']},
                fragment='beak'
            )).getquerydict()
        )
