def split_line(line):
    splited_line = line.split()
    return splited_line


def index_line(array, elem):
    _index = array.index(elem)
    return _index


def split_by_symbol(line, symbol):
    _index = line.split(symbol)
    return _index


def parse_cookie(cookie):
    for chunk in cookie.split(';'):
        if '=' in chunk:
            key, val = chunk.split('=', 1)
        else:
            key, val = '', chunk
    return key, val
