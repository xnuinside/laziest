def str_generator():
    return 'random_string'


def int_generator():
    return 123


def float_generator():
    return 0.7


def dict_generator():
    return {}


def list_generator():
    return []


def tuple_generator():
    return ()


def set_generator():
    return {}


def obj_generator():
    class Empty:
        pass
    return Empty()
