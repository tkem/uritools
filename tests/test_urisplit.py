from __future__ import unicode_literals

import unittest

from uritools import urisplit


class UriSplitTest(unittest.TestCase):

    def check(self, uri, parts, decoded=None):
        result = urisplit(uri)
        self.assertEqual(result, parts, 'Error parsing %r' % uri)
        self.assertEqual(result.geturi(), uri, 'Error recomposing %r' % uri)

    def test_rfc3986(self):
        """urisplit test cases from [RFC3986] 3. Syntax Components"""
        cases = [
            ('foo://example.com:8042/over/there?name=ferret#nose',
             ('foo', 'example.com:8042', '/over/there', 'name=ferret',
              'nose')),
            ('urn:example:animal:ferret:nose',
             ('urn', None, 'example:animal:ferret:nose', None, None)),
            (b'foo://example.com:8042/over/there?name=ferret#nose',
             (b'foo', b'example.com:8042', b'/over/there', b'name=ferret',
              b'nose')),
            (b'urn:example:animal:ferret:nose',
             (b'urn', None, b'example:animal:ferret:nose', None, None)),
        ]
        for uri, parts in cases:
            self.check(uri, parts)

    def test_abnormal(self):
        cases = [
            ('', (None, None, '', None, None)),
            (':', (None, None, ':', None, None)),
            (':/', (None, None, ':/', None, None)),
            ('://', (None, None, '://', None, None)),
            ('://?', (None, None, '://', '', None)),
            ('://#', (None, None, '://', None, '')),
            ('://?#', (None, None, '://', '', '')),
            ('//', (None, '', '', None, None)),
            ('///', (None, '', '/', None, None)),
            ('//?', (None, '', '', '', None)),
            ('//#', (None, '', '', None, '')),
            ('//?#', (None, '', '', '', '')),
            ('?', (None, None, '', '', None)),
            ('??', (None, None, '', '?', None)),
            ('?#', (None, None, '', '', '')),
            ('#', (None, None, '', None, '')),
            ('##', (None, None, '', None, '#')),
            (b'', (None, None, b'', None, None)),
            (b':', (None, None, b':', None, None)),
            (b':/', (None, None, b':/', None, None)),
            (b'://', (None, None, b'://', None, None)),
            (b'://?', (None, None, b'://', b'', None)),
            (b'://#', (None, None, b'://', None, b'')),
            (b'://?#', (None, None, b'://', b'', b'')),
            (b'//', (None, b'', b'', None, None)),
            (b'///', (None, b'', b'/', None, None)),
            (b'//?', (None, b'', b'', b'', None)),
            (b'//#', (None, b'', b'', None, b'')),
            (b'//?#', (None, b'', b'', b'', b'')),
            (b'?', (None, None, b'', b'', None)),
            (b'??', (None, None, b'', b'?', None)),
            (b'?#', (None, None, b'', b'', b'')),
            (b'#', (None, None, b'', None, b'')),
            (b'##', (None, None, b'', None, b'#')),
        ]
        for uri, parts in cases:
            self.check(uri, parts)

    def test_members(self):
        uri = 'foo://user@example.com:8042/over/there?name=ferret#nose'
        result = urisplit(uri)
        self.assertEqual(result.scheme, 'foo')
        self.assertEqual(result.authority, 'user@example.com:8042')
        self.assertEqual(result.path, '/over/there')
        self.assertEqual(result.query, 'name=ferret')
        self.assertEqual(result.fragment, 'nose')
        self.assertEqual(result.userinfo, 'user')
        self.assertEqual(result.host, 'example.com')
        self.assertEqual(result.port, '8042')
        self.assertEqual(result.geturi(), uri)
        self.assertEqual(result.getscheme(), 'foo')
        self.assertEqual(result.getauthority(), 'user@example.com:8042')
        self.assertEqual(result.getpath(), '/over/there')
        self.assertEqual(result.getquery(), 'name=ferret')
        self.assertEqual(result.getfragment(), 'nose')
        self.assertEqual(result.getuserinfo(), 'user')
        self.assertEqual(result.gethost(), 'example.com')
        self.assertEqual(result.gethostip(), 'example.com')
        self.assertEqual(result.getport(), 8042)
        self.assertEqual(dict(result.getquerydict()), {'name': ['ferret']})
        self.assertEqual(list(result.getquerylist()), [('name', 'ferret')])

        uri = 'urn:example:animal:ferret:nose'
        result = urisplit(uri)
        self.assertEqual(result.scheme, 'urn')
        self.assertEqual(result.authority, None)
        self.assertEqual(result.path, 'example:animal:ferret:nose')
        self.assertEqual(result.query, None)
        self.assertEqual(result.fragment, None)
        self.assertEqual(result.userinfo, None)
        self.assertEqual(result.host, None)
        self.assertEqual(result.port, None)
        self.assertEqual(result.geturi(), uri)
        self.assertEqual(result.getscheme(), 'urn')
        self.assertEqual(result.getauthority(), None)
        self.assertEqual(result.getpath(), 'example:animal:ferret:nose')
        self.assertEqual(result.getquery(), None)
        self.assertEqual(result.getfragment(), None)
        self.assertEqual(result.getuserinfo(), None)
        self.assertEqual(result.gethost(), None)
        self.assertEqual(result.gethostip(), None)
        self.assertEqual(result.getport(), None)
        self.assertEqual(dict(result.getquerydict()), {})
        self.assertEqual(list(result.getquerylist()), [])

        uri = b'foo://user@example.com:8042/over/there?name=ferret#nose'
        result = urisplit(uri)
        self.assertEqual(result.scheme, b'foo')
        self.assertEqual(result.authority, b'user@example.com:8042')
        self.assertEqual(result.path, b'/over/there')
        self.assertEqual(result.query, b'name=ferret')
        self.assertEqual(result.fragment, b'nose')
        self.assertEqual(result.userinfo, b'user')
        self.assertEqual(result.host, b'example.com')
        self.assertEqual(result.port, b'8042')
        self.assertEqual(result.geturi(), uri)
        self.assertEqual(result.getscheme(), 'foo')
        self.assertEqual(result.getauthority(), 'user@example.com:8042')
        self.assertEqual(result.getpath(), '/over/there')
        self.assertEqual(result.getquery(), 'name=ferret')
        self.assertEqual(result.getfragment(), 'nose')
        self.assertEqual(result.getuserinfo(), 'user')
        self.assertEqual(result.gethost(), 'example.com')
        self.assertEqual(result.gethostip(), 'example.com')
        self.assertEqual(result.getport(), 8042)
        self.assertEqual(dict(result.getquerydict()), {'name': ['ferret']})
        self.assertEqual(list(result.getquerylist()), [('name', 'ferret')])

        uri = b'urn:example:animal:ferret:nose'
        result = urisplit(uri)
        self.assertEqual(result.scheme, b'urn')
        self.assertEqual(result.authority, None)
        self.assertEqual(result.path, b'example:animal:ferret:nose')
        self.assertEqual(result.query, None)
        self.assertEqual(result.fragment, None)
        self.assertEqual(result.userinfo, None)
        self.assertEqual(result.host, None)
        self.assertEqual(result.port, None)
        self.assertEqual(result.geturi(), uri)
        self.assertEqual(result.getscheme(), 'urn')
        self.assertEqual(result.getauthority(), None)
        self.assertEqual(result.getpath(), 'example:animal:ferret:nose')
        self.assertEqual(result.getquery(), None)
        self.assertEqual(result.getfragment(), None)
        self.assertEqual(result.getuserinfo(), None)
        self.assertEqual(result.gethost(), None)
        self.assertEqual(result.gethostip(), None)
        self.assertEqual(result.getport(), None)
        self.assertEqual(dict(result.getquerydict()), {})
        self.assertEqual(list(result.getquerylist()), [])

    def test_getscheme(self):
        self.assertEqual(urisplit('foo').getscheme(default='bar'), 'bar')
        self.assertEqual(urisplit('FOO_BAR:/').getscheme(), 'foo_bar')
        self.assertEqual(urisplit(b'foo').getscheme(default='bar'), 'bar')
        self.assertEqual(urisplit(b'FOO_BAR:/').getscheme(), 'foo_bar')

    def test_gethostip(self):
        from ipaddress import IPv4Address, IPv6Address
        cases = [
            ('http://Test.python.org:5432/foo/', 'test.python.org'),
            ('http://12.34.56.78:5432/foo/', IPv4Address('12.34.56.78')),
            ('http://[::1]:5432/foo/', IPv6Address('::1')),
        ]
        for uri, hostip in cases:
            self.assertEqual(urisplit(uri).gethostip(), hostip)
            self.assertEqual(urisplit(uri.encode()).gethostip(), hostip)

    def test_getaddrinfo(self):
        import socket
        family = socket.AF_INET
        socktype = socket.SOCK_STREAM
        proto = socket.getprotobyname('tcp')

        cases = [
            ((family, socktype, proto, '', ('127.0.0.1', 80)),
             'http://localhost/foo',
             None),
            ((family, socktype, proto, '', ('127.0.0.1', 8080)),
             'http://localhost/foo',
             8080),
            ((family, socktype, proto, '', ('127.0.0.1', 8000)),
             'http://localhost:8000/foo',
             None),
            ((family, socktype, proto, '', ('127.0.0.1', 8000)),
             'http://localhost:8000/foo',
             8080),
            ((family, socktype, proto, '', ('127.0.0.1', 0)),
             'foo://user@localhost/foo',
             None),
            ((family, socktype, proto, '', ('127.0.0.1', 8080)),
             'foo://user@localhost/foo',
             8080),
            ((family, socktype, proto, '', ('127.0.0.1', 8000)),
             'foo://user@localhost:8000/foo',
             None),
            ((family, socktype, proto, '', ('127.0.0.1', 8000)),
             'foo://user@localhost:8000/foo',
             8080),
        ]

        for addrinfo, uri, port in cases:
            self.assertIn(addrinfo, urisplit(uri).getaddrinfo(port=port))

    def test_defaultport(self):
        for uri in ['foo://bar', 'foo://bar:', 'foo://bar/', 'foo://bar:/']:
            result = urisplit(uri)
            if result.authority.endswith(':'):
                self.assertEqual(result.port, '')
            else:
                self.assertEqual(result.port, None)
            self.assertEqual(result.gethost(), 'bar')
            self.assertEqual(result.getport(8000), 8000)

    def test_getquery(self):
        cases = [
            ("?", [], {}),
            ("?&", [], {}),
            ("?&&", [], {}),
            ("?=",
             [('', '')],
             {'': ['']}),
            ("?=a",
             [('', 'a')],
             {'': ['a']}),
            ("?a",
             [('a', None)],
             {'a': [None]}),
            ("?a=",
             [('a', '')],
             {'a': ['']}),
            ("?&a=b",
             [('a', 'b')],
             {'a': ['b']}),
            ("?a=a+b&b=b+c",
             [('a', 'a+b'), ('b', 'b+c')],
             {'a': ['a+b'], 'b': ['b+c']}),
            ("?a=a%20b&b=b%20c",
             [('a', 'a b'), ('b', 'b c')],
             {'a': ['a b'], 'b': ['b c']}),
            ("?a=1&a=2",
             [('a', '1'), ('a', '2')],
             {'a': ['1', '2']}),
        ]
        for query, querylist, querydict in cases:
            self.assertEqual(urisplit(query).getquerylist(), querylist,
                             'Error parsing query dict for %r' % query)
            self.assertEqual(urisplit(query).getquerydict(), querydict,
                             'Error parsing query list for %r' % query)

    def test_ip_literal(self):
        cases = [
            ('http://Test.python.org:5432/foo/', 'test.python.org', 5432),
            ('http://12.34.56.78:5432/foo/', '12.34.56.78', 5432),
            ('http://[::1]:5432/foo/', '::1', 5432),
            ('http://[dead:beef::1]:5432/foo/', 'dead:beef::1', 5432),
            ('http://[dead:beef::]:5432/foo/', 'dead:beef::', 5432),
            ('http://[dead:beef:cafe:5417:affe:8FA3:deaf:feed]:5432/foo/',
             'dead:beef:cafe:5417:affe:8fa3:deaf:feed', 5432),
            ('http://[::12.34.56.78]:5432/foo/', '::12.34.56.78', 5432),
            ('http://[::ffff:12.34.56.78]:5432/foo/',
             '::ffff:12.34.56.78', 5432),
            ('http://Test.python.org/foo/', 'test.python.org', None),
            ('http://12.34.56.78/foo/', '12.34.56.78', None),
            ('http://[::1]/foo/', '::1', None),
            ('http://[dead:beef::1]/foo/', 'dead:beef::1', None),
            ('http://[dead:beef::]/foo/', 'dead:beef::', None),
            ('http://[dead:beef:cafe:5417:affe:8FA3:deaf:feed]/foo/',
             'dead:beef:cafe:5417:affe:8fa3:deaf:feed', None),
            ('http://[::12.34.56.78]/foo/', '::12.34.56.78', None),
            ('http://[::ffff:12.34.56.78]/foo/',
             '::ffff:12.34.56.78', None),
            ('http://Test.python.org:/foo/', 'test.python.org', None),
            ('http://12.34.56.78:/foo/', '12.34.56.78', None),
            ('http://[::1]:/foo/', '::1', None),
            ('http://[dead:beef::1]:/foo/', 'dead:beef::1', None),
            ('http://[dead:beef::]:/foo/', 'dead:beef::', None),
            ('http://[dead:beef:cafe:5417:affe:8FA3:deaf:feed]:/foo/',
             'dead:beef:cafe:5417:affe:8fa3:deaf:feed', None),
            ('http://[::12.34.56.78]:/foo/', '::12.34.56.78', None),
            ('http://[::ffff:12.34.56.78]:/foo/',
             '::ffff:12.34.56.78', None),
            ]
        for uri, host, port in cases:
            parts = urisplit(uri)
            self.assertEqual((host, port), (parts.gethost(), parts.getport()))
            parts = urisplit(uri.encode('ascii'))
            self.assertEqual((host, port), (parts.gethost(), parts.getport()))

    def test_invalid_ip_literal(self):
        uris = [
            'http://::12.34.56.78]/',
            'http://[::1/foo/',
            'ftp://[::1/foo/bad]/bad',
            'http://[::1/foo/bad]/bad',
            'http://[foo]/',
            'http://[v7.future]'
        ]
        for uri in uris:
            with self.assertRaises(ValueError, msg='%r' % uri):
                urisplit(uri).gethost()
            with self.assertRaises(ValueError, msg='%r' % uri):
                urisplit(uri).gethostip()
            with self.assertRaises(ValueError, msg='%r' % uri.encode('ascii')):
                urisplit(uri.encode('ascii')).gethost()
