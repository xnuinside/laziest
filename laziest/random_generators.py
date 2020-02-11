# TODO: temporary, after need to integrate with hypothesis or smth else to generate values
from typing import Dict, Text, List
from random import random, randint


def map_types(_type, slices=None):
    if _type == Text or _type == str:
        return str_generator()
    elif _type == dict or _type == Dict:
        return dict_generator(slices)
    elif _type == float:
        return float_generator()
    elif _type == int:
        return int_generator()
    elif _type == list or _type == List:
        return list_generator()
    else:
        print(_type)
        return 'need_to_define_generator'


def str_generator():
    return 'random_string'


def int_generator():
    return randint(0, 15)


def float_generator():
    return random()


def dict_generator(keys=None):
    _dict = {}
    if keys:
        print(keys)
        for key in keys:
            print(keys)
            _dict.update({key: map_types(keys[key]['type'])})
    return _dict


def list_generator(max_index: int = 1, elem_types=None):
    # TODO: can be different types in one list in different indexes
    list_output = []
    for i in range(max_index):
        if not elem_types:
            elem_types = int
        list_output.append(map_types(elem_types))
    return list_output


def tuple_generator():
    return ()


def set_generator():
    return {}


def obj_generator():
    class Empty:
        pass
    return Empty()
