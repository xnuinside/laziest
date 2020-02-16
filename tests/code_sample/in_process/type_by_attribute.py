def split_line(line):
    splitted_line = line.split()
    return splitted_line


def index_line(array, elem):
    _index = array.index(elem)
    return _index


def parse_cookie(cookie):
    cookiedict = {}
    for chunk in cookie.split(';'):
        if '=' in chunk:
            key, val = chunk.split('=', 1)
        else:
            key, val = '', chunk
        key, val = key.strip(), val.strip()
        if key or val:
            cookiedict[key] = val
    return cookiedict
