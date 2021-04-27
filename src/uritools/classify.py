from .split import urisplit

# TODO: use specialized checks/regexes for performance


def isuri(uristring):
    """Return :const:`True` if `uristring` is a URI."""
    return urisplit(uristring).isuri()


def isabsuri(uristring):
    """Return :const:`True` if `uristring` is an absolute URI."""
    return urisplit(uristring).isabsuri()


def isnetpath(uristring):
    """Return :const:`True` if `uristring` is a network-path reference."""
    return urisplit(uristring).isnetpath()


def isabspath(uristring):
    """Return :const:`True` if `uristring` is an absolute-path reference."""
    return urisplit(uristring).isabspath()


def isrelpath(uristring):
    """Return :const:`True` if `uristring` is a relative-path reference."""
    return urisplit(uristring).isrelpath()


def issamedoc(uristring):
    """Return :const:`True` if `uristring` is a same-document reference."""
    return urisplit(uristring).issamedoc()
