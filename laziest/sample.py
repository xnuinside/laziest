def one_condition_custom_exception(arg1):
    if arg1 == '1':
        raise Exception('we hate 1')
    elif arg1 > 2:
        print(f'{arg1} more when 2')
    return arg1

def one_condition_custom_exception_2(arg1):
    if arg1 == '1':
        raise Exception('we hate 1')
    elif arg1 > 2:
        print(f'{arg1} more when 2')
    else:
        return arg1
