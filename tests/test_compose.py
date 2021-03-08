import ipaddress
import unittest

from uritools import uricompose


class ComposeTest(unittest.TestCase):
    def check(self, uri, **kwargs):
        result = uricompose(**kwargs)
        self.assertEqual(
            uri, result, msg="%r != %r (kwargs=%r)" % (uri, result, kwargs)
        )

    def test_rfc3986(self):
        """uricompose test cases from [RFC3986] 3. Syntax Components"""
        self.check(
            "foo://example.com:42/over/there?name=ferret#nose",
            scheme="foo",
            authority="example.com:42",
            path="/over/there",
            query="name=ferret",
            fragment="nose",
        )
        self.check(
            "urn:example:animal:ferret:nose",
            scheme="urn",
            path="example:animal:ferret:nose",
        )

    def test_scheme(self):
        cases = [
            ("foo+bar:", "foo+bar"),
            ("foo+bar:", b"foo+bar"),
            ("foo+bar:", "FOO+BAR"),
            ("foo+bar:", b"FOO+BAR"),
        ]
        for uri, scheme in cases:
            self.check(uri, scheme=scheme)
        # invalid scheme
        for scheme in ("", "foo:", "\xf6lk\xfcrbis"):
            with self.assertRaises(ValueError, msg="scheme=%r" % scheme):
                uricompose(scheme=scheme)

    def test_authority(self):
        cases = [
            ("", None),
            ("//", ""),
            ("//", b""),
            ("//example.com", "example.com"),
            ("//example.com", b"example.com"),
            ("//example.com", "example.com:"),
            ("//example.com", b"example.com:"),
            ("//user@example.com", "user@example.com"),
            ("//user@example.com", b"user@example.com"),
            ("//example.com:42", "example.com:42"),
            ("//example.com:42", b"example.com:42"),
            ("//user@example.com:42", "user@example.com:42"),
            ("//user@example.com:42", b"user@example.com:42"),
            ("//user@127.0.0.1:42", "user@127.0.0.1:42"),
            ("//user@127.0.0.1:42", b"user@127.0.0.1:42"),
            ("//user@[::1]:42", "user@[::1]:42"),
            ("//user@[::1]:42", b"user@[::1]:42"),
            ("//user:c2VjcmV0@example.com", "user:c2VjcmV0@example.com"),
            ("//user:c2VjcmV0@example.com", b"user:c2VjcmV0@example.com"),
        ]
        for uri, authority in cases:
            self.check(uri, authority=authority)
        # invalid authority type
        for authority in (True, 42, 3.14, ipaddress.IPv6Address("::1")):
            with self.assertRaises(TypeError, msg="authority=%r" % authority):
                uricompose(authority=authority)

    def test_authority_kwargs(self):
        from ipaddress import IPv4Address, IPv6Address

        cases = [
            ("", [None, None, None]),
            ("//", [None, "", None]),
            ("//", [None, b"", None]),
            ("//example.com", [None, "example.com", None]),
            ("//example.com", [None, b"example.com", None]),
            ("//example.com", [None, "example.com", ""]),
            ("//example.com", [None, "example.com", b""]),
            ("//user@example.com", ["user", "example.com", None]),
            ("//user@example.com", [b"user", "example.com", None]),
            ("//user@example.com", [b"user", b"example.com", None]),
            ("//example.com:42", [None, "example.com", "42"]),
            ("//example.com:42", [None, b"example.com", "42"]),
            ("//example.com:42", [None, b"example.com", b"42"]),
            ("//example.com:42", [None, "example.com", 42]),
            ("//example.com:42", [None, b"example.com", 42]),
            ("//user@example.com:42", ["user", "example.com", "42"]),
            ("//user@example.com:42", [b"user", "example.com", "42"]),
            ("//user@example.com:42", [b"user", b"example.com", "42"]),
            ("//user@example.com:42", [b"user", b"example.com", b"42"]),
            ("//user@example.com:42", ["user", "example.com", 42]),
            ("//user@example.com:42", [b"user", "example.com", 42]),
            ("//user@example.com:42", [b"user", b"example.com", 42]),
            ("//user@127.0.0.1:42", ["user", "127.0.0.1", 42]),
            ("//user@127.0.0.1:42", ["user", b"127.0.0.1", 42]),
            ("//user@127.0.0.1:42", ["user", IPv4Address("127.0.0.1"), 42]),
            ("//user@[::1]:42", ["user", "::1", 42]),
            ("//user@[::1]:42", ["user", b"::1", 42]),
            ("//user@[::1]:42", ["user", "[::1]", 42]),
            ("//user@[::1]:42", ["user", b"[::1]", 42]),
            ("//user@[::1]:42", ["user", IPv6Address("::1"), 42]),
        ]
        for uri, authority in cases:
            self.check(uri, authority=authority)
            userinfo, host, port = authority
            self.check(uri, userinfo=userinfo, host=host, port=port)
        # invalid authority value
        for authority in ([], ["foo"], ["foo", "bar"], range(4)):
            with self.assertRaises(ValueError, msg="authority=%r" % authority):
                uricompose(authority=authority)
        # invalid host type
        for host in (True, 42, 3.14, ipaddress.IPv6Network("2001:db00::0/24")):
            with self.assertRaises(AttributeError, msg="host=%r" % host):
                uricompose(authority=[None, host, None])
            with self.assertRaises(AttributeError, msg="host=%r" % host):
                uricompose(host=host)
        # invalid host ip-literal
        for host in ("[foo]", "[v1.x]"):
            with self.assertRaises(ValueError, msg="host=%r" % host):
                uricompose(authority=[None, host, None])
            with self.assertRaises(ValueError, msg="host=%r" % host):
                uricompose(host=host)
        # invalid port value
        for port in (-1, "foo", 3.14):
            with self.assertRaises(ValueError, msg="port=%r" % port):
                uricompose(authority=[None, "", port])
            with self.assertRaises(ValueError, msg="port=%r" % port):
                uricompose(port=port)

    def test_authority_override(self):
        cases = [
            ("//user@example.com:42", None, "user", "example.com", 42),
            ("//user@example.com:42", "", "user", "example.com", 42),
            ("//user@example.com:42", "example.com", "user", None, 42),
            ("//user@example.com:42", "user@:42", None, "example.com", None),
        ]
        for uri, authority, userinfo, host, port in cases:
            self.check(
                uri, authority=authority, userinfo=userinfo, host=host, port=port
            )

    def test_host_lowercase(self):
        cases = [
            ("//hostname", "HostName"),
            ("//[2001:db8::1]", "[2001:DB8::1]"),
            (
                "//uuid%3A228f0766-a241-4050-a7a8-2c153073e3d7",
                "UUID:228F0766-A241-4050-A7A8-2C153073E3D7",
            ),
        ]
        for uri, host in cases:
            self.check(uri, host=host)

    def test_path(self):
        cases = [
            ("foo", "foo"),
            ("foo", b"foo"),
            ("foo+bar", "foo+bar"),
            ("foo+bar", b"foo+bar"),
            ("foo%20bar", "foo bar"),
            ("foo%20bar", b"foo bar"),
            ("./this:that", "this:that"),
            ("./this:that", b"this:that"),
            ("./this:that/", "this:that/"),
            ("./this:that/", b"this:that/"),
        ]
        for uri, path in cases:
            self.check(uri, path=path)
        # invalid path with authority
        for path in ("foo", b"foo"):
            with self.assertRaises(ValueError, msg="path=%r" % path):
                uricompose(authority="auth", path=path)
        # invalid path without authority
        for path in ("//", b"//", "//foo", b"//foo"):
            with self.assertRaises(ValueError, msg="path=%r" % path):
                uricompose(path=path)

    def test_query(self):
        from collections import OrderedDict as od

        cases = [
            ("?", ""),
            ("?", b""),
            ("?", []),
            ("?", {}),
            ("?name", "name"),
            ("?name", b"name"),
            ("?name", [("name", None)]),
            ("?name", [(b"name", None)]),
            ("?name", {"name": None}),
            ("?name", {b"name": None}),
            ("?name=foo", "name=foo"),
            ("?name=foo", b"name=foo"),
            ("?name=foo", [("name", "foo")]),
            ("?name=foo", [("name", b"foo")]),
            ("?name=foo", [(b"name", b"foo")]),
            ("?name=foo", {"name": "foo"}),
            ("?name=foo", {"name": b"foo"}),
            ("?name=foo", {"name": ["foo"]}),
            ("?name=foo", {"name": [b"foo"]}),
            ("?name=foo", {b"name": b"foo"}),
            ("?name=foo", {b"name": [b"foo"]}),
            ("?name=42", [("name", 42)]),
            ("?name=42", {"name": 42}),
            ("?name=42", {"name": [42]}),
            ("?name=foo&type=bar", [("name", "foo"), ("type", "bar")]),
            ("?name=foo&type=bar", od([("name", "foo"), ("type", "bar")])),
            ("?name=foo&name=bar", [("name", "foo"), ("name", "bar")]),
            ("?name=foo&name=bar", {"name": ["foo", "bar"]}),
            ("?name=a/b/c", dict(name="a/b/c")),
            ("?name=a:b:c", dict(name="a:b:c")),
            ("?name=a?b?c", dict(name="a?b?c")),
            ("?name=a@b@c", dict(name="a@b@c")),
            ("?name=a;b;c", dict(name="a;b;c")),
            ("?name=a%23b%23c", dict(name="a#b#c")),
            ("?name=a%26b%26c", dict(name="a&b&c")),
        ]
        for uri, query in cases:
            self.check(uri, query=query)
        # invalid query type
        for query in (0, [1]):
            with self.assertRaises(TypeError, msg="query=%r" % query):
                uricompose(query=query)

    def test_query_sep(self):
        cases = [
            ("&", "?x=foo&y=bar", [("x", "foo"), ("y", "bar")]),
            (";", "?x=foo;y=bar", [("x", "foo"), ("y", "bar")]),
            ("&", "?x=foo;y=bar", [("x", "foo;y=bar")]),
            (";", "?x=foo&y=bar", [("x", "foo&y=bar")]),
        ]
        for sep, uri, query in cases:
            self.check(uri, query=query, querysep=sep)
