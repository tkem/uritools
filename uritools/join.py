from .split import urisplit


def urijoin(base, ref, strict=False):
    """Convert a URI reference relative to a base URI to its target URI
    string.

    """
    if isinstance(base, type(ref)):
        return urisplit(base).transform(ref, strict).geturi()
    elif isinstance(base, bytes):
        return urisplit(base.decode()).transform(ref, strict).geturi()
    else:
        return urisplit(base).transform(ref.decode(), strict).geturi()
