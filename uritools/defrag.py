from __future__ import unicode_literals

from .encoding import uridecode

import collections


class DefragResult(collections.namedtuple('DefragResult', 'uri fragment')):
    """Class to hold :func:`uridefrag` results.

    Do not try to create instances of this class directly.  Use the
    :func:`uridefrag` factory function instead.

    """

    __slots__ = ()  # prevent creation of instance dictionary

    @property
    def base(self):
        import warnings
        warnings.warn("DefragResult.base is deprecated", DeprecationWarning)
        return self.uri

    def geturi(self):
        """Return the recombined version of the original URI as a string."""
        fragment = self.fragment
        if fragment is None:
            return self.uri
        elif isinstance(fragment, type('')):
            return self.uri + '#' + fragment
        else:
            return self.uri + b'#' + fragment

    def getfragment(self, default=None, encoding='utf-8', errors='strict'):
        """Return the decoded fragment identifier, or `default` if the
        original URI did not contain a fragment component.

        """
        fragment = self.fragment
        if fragment is not None:
            return uridecode(fragment, encoding, errors)
        else:
            return default


def uridefrag(string):
    """Remove an existing fragment component from a URI string.

    The return value is an instance of a subclass of
    :class:`collections.namedtuple` with the following read-only
    attributes:

    +-------------------+-------+---------------------------------------------+
    | Attribute         | Index | Value                                       |
    +===================+=======+=============================================+
    | :attr:`uri`       | 0     | Absolute URI or relative URI reference      |
    |                   |       | without the fragment identifier             |
    +-------------------+-------+---------------------------------------------+
    | :attr:`fragment`  | 1     | Fragment identifier,                        |
    |                   |       | or :const:`None` if not present             |
    +-------------------+-------+---------------------------------------------+

    """
    if isinstance(string, type('')):
        parts = string.partition('#')
    else:
        parts = string.partition(b'#')
    return DefragResult(parts[0], parts[2] if parts[1] else None)
