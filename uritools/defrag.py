import collections

from .encoding import uridecode


class DefragResult(collections.namedtuple('DefragResult', 'uri fragment')):
    """Class to hold :func:`uridefrag` results."""

    __slots__ = ()  # prevent creation of instance dictionary

    def geturi(self):
        """Return the recombined version of the original URI as a string."""
        fragment = self.fragment
        if fragment is None:
            return self.uri
        elif isinstance(fragment, bytes):
            return self.uri + b'#' + fragment
        else:
            return self.uri + u'#' + fragment

    def getfragment(self, default=None, encoding='utf-8', errors='strict'):
        """Return the decoded fragment identifier, or `default` if the
        original URI did not contain a fragment component.

        """
        fragment = self.fragment
        if fragment is not None:
            return uridecode(fragment, encoding, errors)
        else:
            return default


def uridefrag(uristring):
    """Remove an existing fragment component from a URI string."""
    if isinstance(uristring, bytes):
        parts = uristring.partition(b'#')
    else:
        parts = uristring.partition(u'#')
    return DefragResult(parts[0], parts[2] if parts[1] else None)
