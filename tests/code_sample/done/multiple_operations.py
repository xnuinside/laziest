def multiple_assigments_per_line_simple():
    key, val = 'first', 'value of first'
    return key, val


def multiple_assigments_per_line_diff_types():
    key, val = 'first', 6.5
    return key, val


def multiple_assigments_per_line_attr_calls(key, val):
    key, val = key.strip(), val.strip()
    return key, val


def multiple_assigments_per_line_simple_one_return():
    key, _ = 'first', 'value of first'
    return key
