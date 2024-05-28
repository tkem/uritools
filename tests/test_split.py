import unittest

from uritools import urisplit


class SplitTest(unittest.TestCase):
    def check(self, uri, parts, decoded=None):
        result = urisplit(uri)
        self.assertEqual(result, parts, "Error parsing %r" % uri)
        self.assertEqual(result.geturi(), uri, "Error recomposing %r" % uri)

    def test_rfc3986(self):
        """urisplit test cases from [RFC3986] 3. Syntax Components"""
        cases = [
            (
                "foo://example.com:8042/over/there?name=ferret#nose",
                ("foo", "example.com:8042", "/over/there", "name=ferret", "nose"),
            ),
            (
                "urn:example:animal:ferret:nose",
                ("urn", None, "example:animal:ferret:nose", None, None),
            ),
            (
                b"foo://example.com:8042/over/there?name=ferret#nose",
                (b"foo", b"example.com:8042", b"/over/there", b"name=ferret", b"nose"),
            ),
            (
                b"urn:example:animal:ferret:nose",
                (b"urn", None, b"example:animal:ferret:nose", None, None),
            ),
        ]
        for uri, parts in cases:
            self.check(uri, parts)

    def test_abnormal(self):
        cases = [
            ("", (None, None, "", None, None)),
            (":", (None, None, ":", None, None)),
            (":/", (None, None, ":/", None, None)),
            ("://", (None, None, "://", None, None)),
            ("://?", (None, None, "://", "", None)),
            ("://#", (None, None, "://", None, "")),
            ("://?#", (None, None, "://", "", "")),
            ("//", (None, "", "", None, None)),
            ("//:", (None, ":", "", None, None)),
            ("///", (None, "", "/", None, None)),
            ("//?", (None, "", "", "", None)),
            ("//#", (None, "", "", None, "")),
            ("//?#", (None, "", "", "", "")),
            ("?", (None, None, "", "", None)),
            ("??", (None, None, "", "?", None)),
            ("?#", (None, None, "", "", "")),
            ("#", (None, None, "", None, "")),
            ("##", (None, None, "", None, "#")),
            ("?:", (None, None, "", ":", None)),
            ("#:", (None, None, "", None, ":")),
            ("_:", (None, None, "_:", None, None)),
            (b"", (None, None, b"", None, None)),
            (b":", (None, None, b":", None, None)),
            (b":/", (None, None, b":/", None, None)),
            (b"://", (None, None, b"://", None, None)),
            (b"://?", (None, None, b"://", b"", None)),
            (b"://#", (None, None, b"://", None, b"")),
            (b"://?#", (None, None, b"://", b"", b"")),
            (b"//", (None, b"", b"", None, None)),
            (b"//:", (None, b":", b"", None, None)),
            (b"///", (None, b"", b"/", None, None)),
            (b"//?", (None, b"", b"", b"", None)),
            (b"//#", (None, b"", b"", None, b"")),
            (b"//?#", (None, b"", b"", b"", b"")),
            (b"?", (None, None, b"", b"", None)),
            (b"??", (None, None, b"", b"?", None)),
            (b"?#", (None, None, b"", b"", b"")),
            (b"#", (None, None, b"", None, b"")),
            (b"##", (None, None, b"", None, b"#")),
            (b"?:", (None, None, b"", b":", None)),
            (b"#:", (None, None, b"", None, b":")),
            (b"_:", (None, None, b"_:", None, None)),
        ]
        for uri, parts in cases:
            self.check(uri, parts)

    def test_members(self):
        uri = "foo://user@example.com:8042/over/there?name=ferret#nose"
        result = urisplit(uri)
        self.assertEqual(result.scheme, "foo")
        self.assertEqual(result.authority, "user@example.com:8042")
        self.assertEqual(result.path, "/over/there")
        self.assertEqual(result.query, "name=ferret")
        self.assertEqual(result.fragment, "nose")
        self.assertEqual(result.userinfo, "user")
        self.assertEqual(result.host, "example.com")
        self.assertEqual(result.port, "8042")
        self.assertEqual(result.geturi(), uri)
        self.assertEqual(result.getscheme(), "foo")
        self.assertEqual(result.getauthority(), ("user", "example.com", 8042))
        self.assertEqual(result.getuserinfo(), "user")
        self.assertEqual(result.gethost(), "example.com")
        self.assertEqual(result.getport(), 8042)
        self.assertEqual(result.getpath(), "/over/there")
        self.assertEqual(result.getquery(), "name=ferret")
        self.assertEqual(dict(result.getquerydict()), {"name": ["ferret"]})
        self.assertEqual(list(result.getquerylist()), [("name", "ferret")])
        self.assertEqual(result.getfragment(), "nose")

        uri = "urn:example:animal:ferret:nose"
        result = urisplit(uri)
        self.assertEqual(result.scheme, "urn")
        self.assertEqual(result.authority, None)
        self.assertEqual(result.path, "example:animal:ferret:nose")
        self.assertEqual(result.query, None)
        self.assertEqual(result.fragment, None)
        self.assertEqual(result.userinfo, None)
        self.assertEqual(result.host, None)
        self.assertEqual(result.port, None)
        self.assertEqual(result.geturi(), uri)
        self.assertEqual(result.getscheme(), "urn")
        self.assertEqual(result.getauthority(), (None, None, None))
        self.assertEqual(result.getuserinfo(), None)
        self.assertEqual(result.gethost(), None)
        self.assertEqual(result.getport(), None)
        self.assertEqual(result.getpath(), "example:animal:ferret:nose")
        self.assertEqual(result.getquery(), None)
        self.assertEqual(dict(result.getquerydict()), {})
        self.assertEqual(list(result.getquerylist()), [])
        self.assertEqual(result.getfragment(), None)

        uri = "file:///"
        result = urisplit(uri)
        self.assertEqual(result.scheme, "file")
        self.assertEqual(result.authority, "")
        self.assertEqual(result.path, "/")
        self.assertEqual(result.query, None)
        self.assertEqual(result.fragment, None)
        self.assertEqual(result.userinfo, None)
        self.assertEqual(result.host, "")
        self.assertEqual(result.port, None)
        self.assertEqual(result.geturi(), uri)
        self.assertEqual(result.getscheme(), "file")
        self.assertEqual(result.getauthority(), (None, "", None))
        self.assertEqual(result.getuserinfo(), None)
        self.assertEqual(result.gethost(), "")
        self.assertEqual(result.getport(), None)
        self.assertEqual(result.getpath(), "/")
        self.assertEqual(result.getquery(), None)
        self.assertEqual(dict(result.getquerydict()), {})
        self.assertEqual(list(result.getquerylist()), [])
        self.assertEqual(result.getfragment(), None)

        uri = b"foo://user@example.com:8042/over/there?name=ferret#nose"
        result = urisplit(uri)
        self.assertEqual(result.scheme, b"foo")
        self.assertEqual(result.authority, b"user@example.com:8042")
        self.assertEqual(result.path, b"/over/there")
        self.assertEqual(result.query, b"name=ferret")
        self.assertEqual(result.fragment, b"nose")
        self.assertEqual(result.userinfo, b"user")
        self.assertEqual(result.host, b"example.com")
        self.assertEqual(result.port, b"8042")
        self.assertEqual(result.geturi(), uri)
        self.assertEqual(result.getscheme(), "foo")
        self.assertEqual(result.getauthority(), ("user", "example.com", 8042))
        self.assertEqual(result.getuserinfo(), "user")
        self.assertEqual(result.gethost(), "example.com")
        self.assertEqual(result.getport(), 8042)
        self.assertEqual(result.getpath(), "/over/there")
        self.assertEqual(result.getquery(), "name=ferret")
        self.assertEqual(dict(result.getquerydict()), {"name": ["ferret"]})
        self.assertEqual(list(result.getquerylist()), [("name", "ferret")])
        self.assertEqual(result.getfragment(), "nose")

        uri = b"urn:example:animal:ferret:nose"
        result = urisplit(uri)
        self.assertEqual(result.scheme, b"urn")
        self.assertEqual(result.authority, None)
        self.assertEqual(result.path, b"example:animal:ferret:nose")
        self.assertEqual(result.query, None)
        self.assertEqual(result.fragment, None)
        self.assertEqual(result.userinfo, None)
        self.assertEqual(result.host, None)
        self.assertEqual(result.port, None)
        self.assertEqual(result.geturi(), uri)
        self.assertEqual(result.getscheme(), "urn")
        self.assertEqual(result.getauthority(), (None, None, None))
        self.assertEqual(result.getuserinfo(), None)
        self.assertEqual(result.gethost(), None)
        self.assertEqual(result.getport(), None)
        self.assertEqual(result.getpath(), "example:animal:ferret:nose")
        self.assertEqual(result.getquery(), None)
        self.assertEqual(dict(result.getquerydict()), {})
        self.assertEqual(list(result.getquerylist()), [])
        self.assertEqual(result.getfragment(), None)

        uri = b"file:///"
        result = urisplit(uri)
        self.assertEqual(result.scheme, b"file")
        self.assertEqual(result.authority, b"")
        self.assertEqual(result.path, b"/")
        self.assertEqual(result.query, None)
        self.assertEqual(result.fragment, None)
        self.assertEqual(result.userinfo, None)
        self.assertEqual(result.host, b"")
        self.assertEqual(result.port, None)
        self.assertEqual(result.geturi(), uri)
        self.assertEqual(result.getscheme(), "file")
        self.assertEqual(result.getauthority(), (None, "", None))
        self.assertEqual(result.getuserinfo(), None)
        self.assertEqual(result.gethost(), "")
        self.assertEqual(result.getport(), None)
        self.assertEqual(result.getpath(), "/")
        self.assertEqual(result.getquery(), None)
        self.assertEqual(dict(result.getquerydict()), {})
        self.assertEqual(list(result.getquerylist()), [])
        self.assertEqual(result.getfragment(), None)

    def test_getscheme(self):
        self.assertEqual(urisplit("foo").getscheme(default="bar"), "bar")
        self.assertEqual(urisplit("foo:").getscheme(default="bar"), "foo")
        self.assertEqual(urisplit("FOO:").getscheme(default="bar"), "foo")
        self.assertEqual(urisplit("FOO_BAR:/").getscheme(default="x"), "x")
        self.assertEqual(urisplit(b"foo").getscheme(default="bar"), "bar")
        self.assertEqual(urisplit(b"foo:").getscheme(default="bar"), "foo")
        self.assertEqual(urisplit(b"FOO:").getscheme(default="bar"), "foo")
        self.assertEqual(urisplit(b"FOO_BAR:/").getscheme(default="x"), "x")

    def test_getauthority(self):
        from ipaddress import IPv4Address, IPv6Address

        cases = [
            ("urn:example:animal:ferret:nose", None, (None, None, None)),
            ("file:///", None, (None, "", None)),
            (
                "http://userinfo@Test.python.org:5432/foo/",
                None,
                ("userinfo", "test.python.org", 5432),
            ),
            (
                "http://userinfo@12.34.56.78:5432/foo/",
                None,
                ("userinfo", IPv4Address("12.34.56.78"), 5432),
            ),
            (
                "http://userinfo@[::1]:5432/foo/",
                None,
                ("userinfo", IPv6Address("::1"), 5432),
            ),
            (
                "urn:example:animal:ferret:nose",
                ("nobody", "localhost", 42),
                ("nobody", "localhost", 42),
            ),
            ("file:///", ("nobody", "localhost", 42), ("nobody", "localhost", 42)),
            (
                "http://Test.python.org/foo/",
                ("nobody", "localhost", 42),
                ("nobody", "test.python.org", 42),
            ),
            (
                "http://userinfo@Test.python.org/foo/",
                ("nobody", "localhost", 42),
                ("userinfo", "test.python.org", 42),
            ),
            (
                "http://Test.python.org:5432/foo/",
                ("nobody", "localhost", 42),
                ("nobody", "test.python.org", 5432),
            ),
            (
                "http://userinfo@Test.python.org:5432/foo/",
                ("nobody", "localhost", 42),
                ("userinfo", "test.python.org", 5432),
            ),
        ]
        for uri, default, authority in cases:
            self.assertEqual(urisplit(uri).getauthority(default), authority)
        for uri in ["http://[::1/", "http://::1]/"]:
            with self.assertRaises(ValueError, msg="%r" % uri):
                urisplit(uri).getauthority()
            with self.assertRaises(ValueError, msg="%r" % uri):
                urisplit(uri.encode()).getauthority()
        with self.assertRaises(TypeError, msg="%r" % uri):
            urisplit("").getauthority(42)
        with self.assertRaises(ValueError, msg="%r" % uri):
            urisplit("").getauthority(("userinfo", "test.python.org"))

    def test_gethost(self):
        from ipaddress import IPv4Address, IPv6Address

        cases = [
            ("http://Test.python.org:5432/foo/", "test.python.org"),
            ("http://12.34.56.78:5432/foo/", IPv4Address("12.34.56.78")),
            ("http://[::1]:5432/foo/", IPv6Address("::1")),
        ]
        for uri, host in cases:
            self.assertEqual(urisplit(uri).gethost(), host)
            self.assertEqual(urisplit(uri.encode()).gethost(), host)
        for uri in ["http://[::1/", "http://::1]/"]:
            with self.assertRaises(ValueError, msg="%r" % uri):
                urisplit(uri).gethost()
            with self.assertRaises(ValueError, msg="%r" % uri):
                urisplit(uri.encode()).gethost()

    def test_getport(self):
        for uri in ["foo://bar", "foo://bar:", "foo://bar/", "foo://bar:/"]:
            result = urisplit(uri)
            if result.authority.endswith(":"):
                self.assertEqual(result.port, "")
            else:
                self.assertEqual(result.port, None)
            self.assertEqual(result.gethost(), "bar")
            self.assertEqual(result.getport(8000), 8000)

    def test_getpath(self):
        cases = [
            ("", "", "/"),
            (".", "./", "/"),
            ("./", "./", "/"),
            ("./.", "./", "/"),
            ("./..", "../", "/"),
            ("./foo", "foo", "/foo"),
            ("./foo/", "foo/", "/foo/"),
            ("./foo/.", "foo/", "/foo/"),
            ("./foo/..", "./", "/"),
            ("..", "../", "/"),
            ("../", "../", "/"),
            ("../.", "../", "/"),
            ("../..", "../../", "/"),
            ("../foo", "../foo", "/foo"),
            ("../foo/", "../foo/", "/foo/"),
            ("../foo/.", "../foo/", "/foo/"),
            ("../foo/..", "../", "/"),
            ("../../foo", "../../foo", "/foo"),
            ("../../foo/", "../../foo/", "/foo/"),
            ("../../foo/.", "../../foo/", "/foo/"),
            ("../../foo/..", "../../", "/"),
            ("../../foo/../bar", "../../bar", "/bar"),
            ("../../foo/../bar/", "../../bar/", "/bar/"),
            ("../../foo/../bar/.", "../../bar/", "/bar/"),
            ("../../foo/../bar/..", "../../", "/"),
            ("../../foo/../..", "../../../", "/"),
        ]
        for uri, relpath, abspath in cases:
            parts = urisplit(uri)
            self.assertEqual(relpath, parts.getpath())
            parts = urisplit(uri.encode("ascii"))
            self.assertEqual(relpath, parts.getpath())
            parts = urisplit("/" + uri)
            self.assertEqual(abspath, parts.getpath())
            parts = urisplit(("/" + uri).encode("ascii"))
            self.assertEqual(abspath, parts.getpath())

    def test_getquery(self):
        cases = [
            ("", [], {}),
            ("?", [], {}),
            ("?&", [], {}),
            ("?&&", [], {}),
            ("?=", [("", "")], {"": [""]}),
            ("?=a", [("", "a")], {"": ["a"]}),
            ("?a", [("a", None)], {"a": [None]}),
            ("?a=", [("a", "")], {"a": [""]}),
            ("?&a=b", [("a", "b")], {"a": ["b"]}),
            (
                "?a=a+b&b=b+c",
                [("a", "a+b"), ("b", "b+c")],
                {"a": ["a+b"], "b": ["b+c"]},
            ),
            (
                "?a=a%20b&b=b%20c",
                [("a", "a b"), ("b", "b c")],
                {"a": ["a b"], "b": ["b c"]},
            ),
            ("?a=1&a=2", [("a", "1"), ("a", "2")], {"a": ["1", "2"]}),
        ]
        for query, querylist, querydict in cases:
            parts = urisplit(query)
            self.assertEqual(
                parts.getquerylist(),
                querylist,
                "Error parsing query dict for %r" % query,
            )
            self.assertEqual(
                parts.getquerydict(),
                querydict,
                "Error parsing query list for %r" % query,
            )

    def test_getquerysep(self):
        cases = [
            ("&", "?a=b", [("a", "b")]),
            (";", "?a=b", [("a", "b")]),
            ("&", "?a=a+b&b=b+c", [("a", "a+b"), ("b", "b+c")]),
            (";", "?a=a+b;b=b+c", [("a", "a+b"), ("b", "b+c")]),
            ("&", "?a=a+b;b=b+c", [("a", "a+b;b=b+c")]),
            (";", "?a=a+b&b=b+c", [("a", "a+b&b=b+c")]),
            ("&", "?a&b", [("a", None), ("b", None)]),
            (";", "?a;b", [("a", None), ("b", None)]),
            (b"&", "?a&b", [("a", None), ("b", None)]),
            ("&", b"?a&b", [("a", None), ("b", None)]),
        ]
        for sep, query, querylist in cases:
            parts = urisplit(query)
            self.assertEqual(
                parts.getquerylist(sep),
                querylist,
                "Error parsing query list for %r" % query,
            )

    def test_ipv4_literal(self):
        cases = [
            ("http://12.34.56.78/foo/", "12.34.56.78", None),
            ("http://12.34.56.78:/foo/", "12.34.56.78", None),
            ("http://12.34.56.78:5432/foo/", "12.34.56.78", 5432),
        ]
        for uri, host, port in cases:
            for parts in (urisplit(uri), urisplit(uri.encode("ascii"))):
                self.assertEqual(host, str(parts.gethost()))
                self.assertEqual(port, parts.getport())

    def test_ipv6_literal(self):
        cases = [
            ("http://[::1]:5432/foo/", "0000:0000:0000:0000:0000:0000:0000:0001", 5432),
            (
                "http://[dead:beef::1]:5432/foo/",
                "dead:beef:0000:0000:0000:0000:0000:0001",
                5432,
            ),
            (
                "http://[dead:beef::]:5432/foo/",
                "dead:beef:0000:0000:0000:0000:0000:0000",
                5432,
            ),
            (
                "http://[dead:beef:cafe:5417:affe:8FA3:deaf:feed]:5432/foo/",
                "dead:beef:cafe:5417:affe:8fa3:deaf:feed",
                5432,
            ),
            ("http://[::1]/foo/", "0000:0000:0000:0000:0000:0000:0000:0001", None),
            (
                "http://[dead:beef::1]/foo/",
                "dead:beef:0000:0000:0000:0000:0000:0001",
                None,
            ),
            (
                "http://[dead:beef::]/foo/",
                "dead:beef:0000:0000:0000:0000:0000:0000",
                None,
            ),
            (
                "http://[dead:beef:cafe:5417:affe:8FA3:deaf:feed]/foo/",
                "dead:beef:cafe:5417:affe:8fa3:deaf:feed",
                None,
            ),
            ("http://[::1]:/foo/", "0000:0000:0000:0000:0000:0000:0000:0001", None),
            (
                "http://[dead:beef::1]:/foo/",
                "dead:beef:0000:0000:0000:0000:0000:0001",
                None,
            ),
            (
                "http://[dead:beef::]:/foo/",
                "dead:beef:0000:0000:0000:0000:0000:0000",
                None,
            ),
            (
                "http://[dead:beef:cafe:5417:affe:8FA3:deaf:feed]:/foo/",
                "dead:beef:cafe:5417:affe:8fa3:deaf:feed",
                None,
            ),
        ]
        for uri, host, port in cases:
            for parts in (urisplit(uri), urisplit(uri.encode("ascii"))):
                self.assertEqual(host, parts.gethost().exploded)
                self.assertEqual(port, parts.getport())

    def test_ipv4_mapped_literal(self):
        # since Python 3.13, the "alternative form" is used for
        # IPv4-mapped addresses, see RFC 4291 2.2 p.3
        cases = [
            (
                "http://[::12.34.56.78]:5432/foo/",
                [
                    "0000:0000:0000:0000:0000:0000:0c22:384e",
                    "0000:0000:0000:0000:0000:0000:12.34.56.78",
                ],
                5432,
            ),
            (
                "http://[::ffff:12.34.56.78]:5432/foo/",
                [
                    "0000:0000:0000:0000:0000:ffff:0c22:384e",
                    "0000:0000:0000:0000:0000:ffff:12.34.56.78",
                ],
                5432,
            ),
            (
                "http://[::12.34.56.78]/foo/",
                [
                    "0000:0000:0000:0000:0000:0000:0c22:384e",
                    "0000:0000:0000:0000:0000:0000:12.34.56.78",
                ],
                None,
            ),
            (
                "http://[::ffff:12.34.56.78]/foo/",
                [
                    "0000:0000:0000:0000:0000:ffff:0c22:384e",
                    "0000:0000:0000:0000:0000:ffff:12.34.56.78",
                ],
                None,
            ),
            (
                "http://[::12.34.56.78]:/foo/",
                [
                    "0000:0000:0000:0000:0000:0000:0c22:384e",
                    "0000:0000:0000:0000:0000:0000:12.34.56.78",
                ],
                None,
            ),
            (
                "http://[::ffff:12.34.56.78]:/foo/",
                [
                    "0000:0000:0000:0000:0000:ffff:0c22:384e",
                    "0000:0000:0000:0000:0000:ffff:12.34.56.78",
                ],
                None,
            ),
        ]
        for uri, hosts, port in cases:
            parts = urisplit(uri)
            self.assertIn(parts.gethost().exploded, hosts)
            self.assertEqual(parts.getport(), port)
            parts = urisplit(uri.encode("ascii"))
            self.assertIn(parts.gethost().exploded, hosts)
            self.assertEqual(parts.getport(), port)

    def test_invalid_ip_literal(self):
        uris = [
            "http://::12.34.56.78]/",
            "http://[::1/foo/",
            "ftp://[::1/foo/bad]/bad",
            "http://[::1/foo/bad]/bad",
            "http://[foo]/",
            "http://[v7.future]",
        ]
        for uri in uris:
            with self.assertRaises(ValueError, msg="%r" % uri):
                urisplit(uri).gethost()
            with self.assertRaises(ValueError, msg="%r" % uri.encode("ascii")):
                urisplit(uri.encode("ascii")).gethost()
