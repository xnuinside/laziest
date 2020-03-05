def multiple_assigment_per_line_attr_calls_one_return(key, val):
    key, _ = key.strip(), val.strip()
    return key


def multiple_assigment_per_line_attr_calls_more_call(key, val, new, line, one_more):
    key, val, new, line, one_more = key.strip(), val.split(), new.strip(), line.split(), one_more.strip()
    return key, val, new, line, one_more
