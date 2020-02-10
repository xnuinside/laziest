# TODO: temporary, after need to integrate with hypothesis or smth else to generate values
from typing import Dict, List, Text
from random import random, randint


def map_types(_type, slices=None):
    if _type == Text or _type == str:
        return str_generator
    elif _type == dict or _type == Dict:
        return dict_generator(slices)
    elif _type == float:
        return float_generator
    elif _type == int:
        return int_generator
    else:
        return 'need_to_define_generator'


def str_generator():
    return 'random_string'


def int_generator():
    return randint(0, 1000)


def float_generator():
    return random()


def dict_generator(keys=None):
    _dict = {}
    if keys:
        print(keys)
        for key in keys:
            _dict.update({key: map_types(keys[key]['type'])()})
    return _dict


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