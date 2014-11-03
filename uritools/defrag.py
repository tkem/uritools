from .encoding import uridecode

import collections
import warnings


class DefragResult(collections.namedtuple('DefragResult', 'base fragment')):
    """Class to hold :func:`uridefrag` results."""

    def geturi(self):
        """Return the recombined version of the original URI as a string."""
        if self.fragment is None:
            return self.base
        elif isinstance(self.fragment, bytes):
            return b'#'.join((self.base, self.fragment))
        else:
            return '#'.join((self.base, self.fragment))

    def getbase(self, encoding='utf-8'):
        """Return the decoded absolute URI or relative URI reference without
        the fragment.

        """
        warnings.warn("deprecated", DeprecationWarning)
        return uridecode(self.base, encoding)

    def getfragment(self, default=None, encoding='utf-8'):
        """Return the decoded fragment identifier, or `default` if the
        original URI did not contain a fragment component.

        """
        if self.fragment is not None:
            return uridecode(self.fragment, encoding)
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
    | :attr:`base`      | 0     | Absoulte URI or relative URI reference      |
    |                   |       | without the fragment identifier             |
    +-------------------+-------+---------------------------------------------+
    | :attr:`fragment`  | 1     | Fragment identifier,                        |
    |                   |       | or :const:`None` if not present             |
    +-------------------+-------+---------------------------------------------+

    """
    parts = string.partition(b'#' if isinstance(string, bytes) else '#')
    if parts[1]:
        return DefragResult(parts[0], parts[2])
    else:
        return DefragResult(parts[0], None)
