from __future__ import unicode_literals

import unittest

from uritools import uricompose


class UriComposeTest(unittest.TestCase):

    def check(self, uri, **kwargs):
        self.assertEqual(uri, uricompose(**kwargs), msg='uri=%r' % uri)

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

    def test_scheme(self):
        cases = [
            (b'foo+bar:', 'foo+bar'),
            (b'foo+bar:', b'foo+bar'),
            (b'foo+bar:', 'FOO+BAR'),
            (b'foo+bar:', b'FOO+BAR'),

        ]
        for uri, scheme in cases:
            self.check(uri, scheme=scheme)
        for scheme in ('', 'foo:', '\xf6lk\xfcrbis'):
            with self.assertRaises(ValueError, msg='scheme=%r' % scheme):
                uricompose(scheme=scheme)

    def test_authority(self):
        cases = [
            (b'//tkem@example.com:8042', 'tkem@example.com:8042'),
            (b'//tkem@example.com:8042', b'tkem@example.com:8042'),
            (b'//tkem@example.com:8042', ('tkem', 'example.com', '8042')),
            (b'//tkem@example.com:8042', ['tkem', 'example.com', '8042']),
            (b'//tkem@example.com:8042', [b'tkem', b'example.com', b'8042']),
            (b'//tkem@example.com:8042', ['tkem', 'example.com', 8042]),
            (b'//tkem@example.com:8042', [b'tkem', b'example.com', 8042]),
            (b'//tkem@example.com', ['tkem', 'example.com', None]),
            (b'//tkem@example.com', [b'tkem', b'example.com', None]),
            (b'//tkem@example.com', ['tkem', 'example.com', '']),
            (b'//tkem@example.com', [b'tkem', b'example.com', '']),
            (b'//tkem:cGFzc3dvcmQ=@foo', ['tkem:cGFzc3dvcmQ=', 'foo', None]),
            (b'//tkem:cGFzc3dvcmQ=@foo', ['tkem:cGFzc3dvcmQ=', 'foo', None]),
            (b'//example.com', [None, 'example.com', None]),
            (b'//example.com', [None, b'example.com', None]),
        ]
        for uri, authority in cases:
            self.check(uri, authority=authority)
        for authority in ([], ['foo'], ['foo', 'bar'], range(4)):
            with self.assertRaises(ValueError, msg='authority=%r' % authority):
                uricompose(authority=authority)
        for authority in (True, 42, 3.14):
            with self.assertRaises(TypeError, msg='authority=%r' % authority):
                uricompose(authority=authority)
        for host in (None, '[foo]', '[::1', '::1]'):
            with self.assertRaises(ValueError, msg='host=%r' % host):
                uricompose(authority=[None, host, None])
        for port in (-1, 'foo', 3.14):
            with self.assertRaises(ValueError, msg='port=%r' % port):
                uricompose(authority=[None, '', port])

    def test_path(self):
        cases = [
            (b'foo', 'foo'),
            (b'foo', b'foo'),
            (b'foo+bar', 'foo+bar'),
            (b'foo+bar', b'foo+bar'),
            (b'foo%20bar', 'foo bar'),
            (b'foo%20bar', b'foo bar'),
        ]
        for uri, path in cases:
            self.check(uri, path=path)
        for path in (None, '//foo', b'//foo', ':/foo', b':/foo'):
            with self.assertRaises(ValueError, msg='path=%r' % path):
                uricompose(path=path)
        for path in ('foo', b'foo'):
            with self.assertRaises(ValueError, msg='path=%r' % path):
                uricompose(authority='auth', path=path)

    def test_query(self):
        from collections import OrderedDict as od

        cases = [
            (b'?', ''),
            (b'?', b''),
            (b'?', []),
            (b'?', {}),
            (b'?name', 'name'),
            (b'?name', b'name'),
            (b'?name', [('name', None)]),
            (b'?name', [(b'name', None)]),
            (b'?name', {'name': None}),
            (b'?name', {b'name': None}),
            (b'?name=foo', 'name=foo'),
            (b'?name=foo', b'name=foo'),
            (b'?name=foo', [('name', 'foo')]),
            (b'?name=foo', [('name', b'foo')]),
            (b'?name=foo', [(b'name', b'foo')]),
            (b'?name=foo', {'name': 'foo'}),
            (b'?name=foo', {'name': b'foo'}),
            (b'?name=foo', {'name': ['foo']}),
            (b'?name=foo', {'name': [b'foo']}),
            (b'?name=foo', {b'name': b'foo'}),
            (b'?name=foo', {b'name': [b'foo']}),
            (b'?name=42', [('name', 42)]),
            (b'?name=42', {'name': 42}),
            (b'?name=42', {'name': [42]}),
            (b'?name=foo&type=bar', [('name', 'foo'), ('type', 'bar')]),
            (b'?name=foo&type=bar', od([('name', 'foo'), ('type', 'bar')])),
            (b'?name=foo&name=bar', [('name', 'foo'), ('name', 'bar')]),
            (b'?name=foo&name=bar', {'name': ['foo', 'bar']}),
        ]
        for uri, query in cases:
            self.check(uri, query=query)
        for query in (0, [1]):
            with self.assertRaises(TypeError, msg='query=%r' % query):
                uricompose(query=query)
