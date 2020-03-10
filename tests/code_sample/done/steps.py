def function_with_args_modifications(arg_1):
    arg_1 *= 10
    arg_1 = str(arg_1) + ' was incremented'
    return arg_1


def function_with_args_modifications_with_function(arg_1):
    arg_1 = arg_1.split()
    return arg_1


def function_with_args_modifications_with_function_and_one_more_step(arg_1):
    arg_1 = arg_1.split()
    arg_1 *= 10
    return arg_1


def multiple_assigment_per_line_attr_calls_one_return(key, val):
    key, new_var = key.strip(), val.strip()
    new_var *= 4
    return new_var


def vars_intersections_steps(key, val):
    key, new_var = key.strip(), val.strip()
    new_var *= 4
    alias_var = key + new_var
    return alias_var

# TODO: add steps with ifs statements
