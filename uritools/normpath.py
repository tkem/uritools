def urinormpath(path):
    """Remove '.' and '..' path segments from a URI path."""

    # RFC 3986 5.2.4. Remove Dot Segments
    out = []
    for s in path.split('/'):
        if s == '.':
            continue
        elif s != '..':
            out.append(s)
        elif out:
            out.pop()
    # Fix leading/trailing slashes
    if path.startswith('/') and (not out or out[0]):
        out.insert(0, '')
    if path.endswith('/.') or path.endswith('/..'):
        out.append('')
    return '/'.join(out)
