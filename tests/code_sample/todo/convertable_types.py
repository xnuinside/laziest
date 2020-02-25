# ta - type annotation
def function_cast_string_ta(arg: str):
    return (1 * 4) * int(arg)


def function_cast_int_ta(arg: int):
    print(f'{str(arg)}')
    return (1 * 4) * arg


def function_cast_list_ta(arg: list):
    arg = tuple(arg)
    return (1 * 4) * arg[0]


# no ta
def function_cast_string(arg):
    return (1 * 4) * int(arg)


def function_cast_int(arg):
    print(f'{str(arg)}')
    return (1 * 4) * arg


def function_cast_list(arg):
    arg = tuple(arg)
    return (1 * 4) * arg[0]



