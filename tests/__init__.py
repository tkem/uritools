def b(string):
    try:
        return string.encode('utf-8')
    except AttributeError:
        return string


def u(string):
    try:
        return string.decode('utf-8')
    except AttributeError:
        return string
