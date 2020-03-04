def include_symbol_in_str(chunk):
    if '=' in chunk:
        key, _ = chunk.split('=', 1)
        return key


def include_symbol_in_str_tuple(chunk):
    if '=' in chunk:
        key, val = chunk.split('=', 1)
        return key, val


def include_list_of_symbols_in_str(chunk):
    for symbol in ['=', ':']:
        if symbol in chunk:
            key, _ = chunk.split('=', 1)
            return key


def include_list_of_symbols_in_str_tuple(chunk):
    for symbol in ['=', ':']:
        if symbol in chunk:
            key, val = chunk.split('=', 1)
            return key, val
