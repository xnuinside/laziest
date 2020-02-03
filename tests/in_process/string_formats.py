def string_format_s(arg1):
    return 'this is %s' % arg1


def string_format(arg1):
    return 'this is {}'.format(arg1)


def string_format_f(arg1):
    return f'this is {arg1}'


def string_format_f_multiple(arg1, arg2, arg3):
    return f'{arg2} this is {arg1}! {arg3}'


def string_format_multiple(arg1, arg2, arg3):
    return ' {} this is {}! {}'.format(arg1, arg2, arg3)


def string_format_named(arg1):
    return 'this is {name}'.format(name=arg1)


def string_format_named_three_args(arg1, arg2, arg3):
    return '{first} this is {name} ! {last}'.format(name=arg1, first=arg2, last=arg3)
