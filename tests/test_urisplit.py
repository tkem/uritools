import unittest

from uritools import urisplit


class UriSplitTest(unittest.TestCase):

    def check(self, uri, split):
        result = urisplit(uri)
        self.assertEqual(result, split)
        self.assertEqual(result.geturi(), uri)

    def test_rfc3986_3(self):
        """urisplit test cases from [RFC3986] 3. Syntax Components"""

        self.check(
            'foo://example.com:8042/over/there?name=ferret#nose',
            ('foo', 'example.com:8042', '/over/there', 'name=ferret', 'nose')
        )
        self.check(
            'urn:example:animal:ferret:nose',
            ('urn', None, 'example:animal:ferret:nose', None, None)
        )

    def test_urlparse_roundtrips(self):
        """urlparse roundtrip test cases"""

        for url, split in [
            ('file:///tmp/junk.txt',
             ('file', '', '/tmp/junk.txt', None, None)),
            ('imap://mail.python.org/mbox1',
             ('imap', 'mail.python.org', '/mbox1', None, None)),
            ('mms://wms.sys.hinet.net/cts/Drama/09006251100.asf',
             ('mms', 'wms.sys.hinet.net', '/cts/Drama/09006251100.asf', None, None)),
            ('svn+ssh://svn.zope.org/repos/main/ZConfig/trunk/',
             ('svn+ssh', 'svn.zope.org', '/repos/main/ZConfig/trunk/', None, None)),
            ('http://www.python.org',
             ('http', 'www.python.org', '', None, None)),
            ('http://www.python.org#abc',
             ('http', 'www.python.org', '', None, 'abc')),
            ('http://www.python.org?q=abc',
             ('http', 'www.python.org', '', 'q=abc', None)),
            ('http://www.python.org/#abc',
             ('http', 'www.python.org', '/', None, 'abc')),
            ('http://a/b/c/d;p?q#f',
             ('http', 'a', '/b/c/d;p', 'q', 'f')),
            ('Python',
             (None, None, 'Python', None, None)),
            ('./Python',
             (None, None, './Python', None, None)),
            ('http://example.com?blahblah=/foo',
             ('http', 'example.com', '', 'blahblah=/foo', None)),
        ]:
            self.check(url, split)

    def test_attributes(self):
        """urlparse attribute test cases"""

        uri = "HTTP://WWW.PYTHON.ORG/doc/#frag"
        p = urisplit(uri)
        #self.assertEqual(p.scheme, "http")
        self.assertEqual(p.authority, "WWW.PYTHON.ORG")
        self.assertEqual(p.path, "/doc/")
        self.assertEqual(p.query, None)
        self.assertEqual(p.fragment, "frag")
        #self.assertEqual(p.username, None)
        #self.assertEqual(p.password, None)
        #self.assertEqual(p.hostname, "www.python.org")
        #self.assertEqual(p.port, None)
        self.assertEqual(p.geturi(), uri)

        uri = "http://User:Pass@www.python.org:080/doc/?query=yes#frag"
        p = urisplit(uri)
        self.assertEqual(p.scheme, "http")
        self.assertEqual(p.authority, "User:Pass@www.python.org:080")
        self.assertEqual(p.path, "/doc/")
        self.assertEqual(p.query, "query=yes")
        self.assertEqual(p.fragment, "frag")
        #self.assertEqual(p.username, "User")
        #self.assertEqual(p.password, "Pass")
        #self.assertEqual(p.hostname, "www.python.org")
        #self.assertEqual(p.port, 80)
        self.assertEqual(p.geturi(), uri)

        uri = "http://User@example.com:Pass@www.python.org:080/doc/?query=yes#frag"
        p = urisplit(uri)
        self.assertEqual(p.scheme, "http")
        self.assertEqual(p.authority, "User@example.com:Pass@www.python.org:080")
        self.assertEqual(p.path, "/doc/")
        self.assertEqual(p.query, "query=yes")
        self.assertEqual(p.fragment, "frag")
        #self.assertEqual(p.username, "User@example.com")
        #self.assertEqual(p.password, "Pass")
        #self.assertEqual(p.hostname, "www.python.org")
        #self.assertEqual(p.port, 80)
        self.assertEqual(p.geturi(), uri)

        uri = "sip:alice@atlanta.com;maddr=239.255.255.1;ttl=15"
        p = urisplit(uri)
        self.assertEqual(p.authority, None)
        #self.assertEqual(p.username, None)
        #self.assertEqual(p.password, None)
        #self.assertEqual(p.hostname, None)
        #self.assertEqual(p.port, None)
        self.assertEqual(p.geturi(), uri)
