def one_condition_standard_exception(arg1):
    if arg1 == '1':
        raise Exception('we hate 1')
    elif arg1 > 2:
        print(f'{arg1} more when 2')
    else:
        return arg1


class CustomException(Exception):
    pass


def one_condition_custom_exception(arg1):
    if arg1 == '1':
        raise CustomException('we hate 1')
    elif arg1 > 2:
        print(f'{arg1} more when 2')
    else:
        return arg1


"""
def one_condition_custom_exception_and_return_binary_op(arg1, arg2, arg3):
    if arg1 == '1':
        raise CustomException('we hate 1')
    elif arg1 > 2:
        print(f'{arg1} more when 2')
        return arg1
    var = 1
    alias = var
    return arg1 * arg2 + arg3, var * arg1 * alias

"""