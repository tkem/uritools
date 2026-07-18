import ipaddress
from collections.abc import Iterable, Mapping, Sequence
from typing import Any, AnyStr, Generic, NamedTuple, overload
from typing_extensions import TypeAlias

__all__ = [
    "GEN_DELIMS",
    "RESERVED",
    "SUB_DELIMS",
    "UNRESERVED",
    "isabspath",
    "isabsuri",
    "isnetpath",
    "isrelpath",
    "issamedoc",
    "isuri",
    "uricompose",
    "uridecode",
    "uridefrag",
    "uriencode",
    "urijoin",
    "urisplit",
    "uriunsplit",
]
__version__: str

GEN_DELIMS: str
SUB_DELIMS: str
RESERVED: str
UNRESERVED: str

@overload
def uriencode(
    uristring: str,
    safe: str | bytes = ...,
    encoding: str = ...,
    errors: str = ...,
) -> bytes: ...
@overload
def uriencode(
    uristring: bytes,
    safe: str | bytes = ...,
    encoding: str | None = ...,
    errors: str = ...,
) -> bytes: ...
@overload
def uridecode(
    uristring: str | bytes,
    encoding: str = ...,
    errors: str = ...,
) -> str: ...
@overload
def uridecode(
    uristring: str | bytes,
    encoding: None,
    errors: str = ...,
) -> bytes: ...

class DefragResult(NamedTuple, Generic[AnyStr]):
    uri: AnyStr
    fragment: AnyStr | None
    def geturi(self) -> AnyStr: ...
    @overload
    def getfragment(
        self,
        default: str | None = ...,
        encoding: str = ...,
        errors: str = ...,
    ) -> str | None: ...
    @overload
    def getfragment(
        self,
        default: bytes | None = ...,
        *,
        encoding: None,
        errors: str = ...,
    ) -> bytes | None: ...

class SplitResult(NamedTuple, Generic[AnyStr]):
    scheme: AnyStr | None
    authority: AnyStr | None
    path: AnyStr
    query: AnyStr | None
    fragment: AnyStr | None
    @property
    def userinfo(self) -> AnyStr | None: ...
    @property
    def host(self) -> AnyStr | None: ...
    @property
    def port(self) -> AnyStr | None: ...
    def geturi(self) -> AnyStr: ...
    def getscheme(self, default: str | None = ...) -> str | None: ...
    @overload
    def getauthority(
        self,
        default: tuple[Any, Any, Any] | None = ...,
        encoding: str = ...,
        errors: str = ...,
    ) -> tuple[
        str | None,
        str | ipaddress.IPv4Address | ipaddress.IPv6Address | None,
        int | None,
    ]: ...
    @overload
    def getauthority(
        self,
        default: tuple[Any, Any, Any] | None = ...,
        *,
        encoding: None,
        errors: str = ...,
    ) -> tuple[
        bytes | None,
        str | ipaddress.IPv4Address | ipaddress.IPv6Address | None,
        int | None,
    ]: ...
    @overload
    def getuserinfo(
        self,
        default: str | None = ...,
        encoding: str = ...,
        errors: str = ...,
    ) -> str | None: ...
    @overload
    def getuserinfo(
        self,
        default: bytes | None = ...,
        *,
        encoding: None,
        errors: str = ...,
    ) -> bytes | None: ...
    def gethost(
        self,
        default: str | ipaddress.IPv4Address | ipaddress.IPv6Address | None = ...,
        errors: str = ...,
    ) -> str | ipaddress.IPv4Address | ipaddress.IPv6Address | None: ...
    def getport(self, default: int | None = ...) -> int | None: ...
    @overload
    def getpath(self, encoding: str = ..., errors: str = ...) -> str: ...
    @overload
    def getpath(self, encoding: None, errors: str = ...) -> bytes: ...
    @overload
    def getquery(
        self,
        default: str | None = ...,
        encoding: str = ...,
        errors: str = ...,
    ) -> str | None: ...
    @overload
    def getquery(
        self,
        default: bytes | None = ...,
        *,
        encoding: None,
        errors: str = ...,
    ) -> bytes | None: ...
    @overload
    def getquerydict(
        self,
        sep: str | bytes = ...,
        encoding: str = ...,
        errors: str = ...,
    ) -> dict[str, list[str | None]]: ...
    @overload
    def getquerydict(
        self,
        sep: str | bytes = ...,
        *,
        encoding: None,
        errors: str = ...,
    ) -> dict[bytes, list[bytes | None]]: ...
    @overload
    def getquerylist(
        self,
        sep: str | bytes = ...,
        encoding: str = ...,
        errors: str = ...,
    ) -> list[tuple[str, str | None]]: ...
    @overload
    def getquerylist(
        self,
        sep: str | bytes = ...,
        *,
        encoding: None,
        errors: str = ...,
    ) -> list[tuple[bytes, bytes | None]]: ...
    @overload
    def getfragment(
        self,
        default: str | None = ...,
        encoding: str = ...,
        errors: str = ...,
    ) -> str | None: ...
    @overload
    def getfragment(
        self,
        default: bytes | None = ...,
        *,
        encoding: None,
        errors: str = ...,
    ) -> bytes | None: ...
    def isuri(self) -> bool: ...
    def isabsuri(self) -> bool: ...
    def isnetpath(self) -> bool: ...
    def isabspath(self) -> bool: ...
    def isrelpath(self) -> bool: ...
    def issamedoc(self) -> bool: ...
    def transform(self, ref: AnyStr, strict: bool = ...) -> SplitResult[AnyStr]: ...

def uridefrag(uristring: AnyStr) -> DefragResult[AnyStr]: ...
def urisplit(uristring: AnyStr) -> SplitResult[AnyStr]: ...
def uriunsplit(parts: Iterable[AnyStr | None]) -> AnyStr: ...
@overload
def urijoin(base: str, ref: str | bytes, strict: bool = ...) -> str: ...
@overload
def urijoin(base: bytes, ref: str, strict: bool = ...) -> str: ...
@overload
def urijoin(base: bytes, ref: bytes, strict: bool = ...) -> bytes: ...
def isuri(uristring: str | bytes) -> bool: ...
def isabsuri(uristring: str | bytes) -> bool: ...
def isnetpath(uristring: str | bytes) -> bool: ...
def isabspath(uristring: str | bytes) -> bool: ...
def isrelpath(uristring: str | bytes) -> bool: ...
def issamedoc(uristring: str | bytes) -> bool: ...

_QueryType: TypeAlias = (
    str | bytes | Mapping[str | bytes, object] | Iterable[tuple[str | bytes, object]]
)

def uricompose(
    scheme: str | bytes | None = ...,
    authority: str
    | bytes
    | Sequence[str | bytes | ipaddress.IPv4Address | ipaddress.IPv6Address | int | None]
    | None = ...,
    path: str | bytes | None = ...,
    query: _QueryType | None = ...,
    fragment: str | bytes | None = ...,
    userinfo: str | bytes | None = ...,
    host: str | bytes | ipaddress.IPv4Address | ipaddress.IPv6Address | None = ...,
    port: int | str | bytes | None = ...,
    querysep: str = ...,
    encoding: str = ...,
) -> str: ...
