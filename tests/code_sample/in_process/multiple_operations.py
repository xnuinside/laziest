"""
def multiple_assigments_per_line_simple():
    key, val = 'first', 'value of first'
    return key, val



def multiple_assigments_per_line_diff_types():
    key, val = 'first', 6.5
    return key, val

"""

def multiple_assigments_per_line_attr_calls(key, val):
    key, val = key.strip(), val.strip()
    return key, val


"""
def multiple_assigments_per_line_simple_one_return():
    key, _ = 'first', 'value of first'
    return key


def multiple_assigments_per_line_attr_calls_one_return(key, val):
    key, _ = key.strip(), val.strip()
    return key


def multiple_assigments_per_line_attr_calls_more_call(key, val, new, line, one_more):
    key, val, new, line, one_more = key.strip(), val.split(), new.strip(), line.split(), one_more.strip()
    return key, val, new, line, one_more
"""