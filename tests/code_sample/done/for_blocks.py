def include_list_of_symbols_in_str_error(chunk):
    for symbol in ['=', ':']:
        if symbol in chunk:
            key, _ = chunk.split('=', 1)
            return key


def include_list_of_symbols_in_str_tuple_error(chunk):
    for symbol in ['=', ':']:
        if symbol in chunk:
            key, val = chunk.split(':', 1)
            return key, val


def include_list_of_symbols_in_str_tuple(chunk):
    for symbol in ['=', ':']:
        if symbol in chunk:
            key, val = chunk.split(symbol, 1)
            return key, val
