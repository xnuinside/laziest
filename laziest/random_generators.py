# TODO: temporary, after need to integrate with hypothesis or smth else to generate values
from typing import Dict, Text, List
from random import random, randint, choice


def map_types(_type, slices=None):
    if isinstance(_type, str):
        _type = eval(_type)
    if _type == Text or _type == str:
        return str_generator()
    elif _type == dict or _type == Dict:
        return dict_generator(slices)
    elif _type == float:
        return float_generator()
    elif _type == int:
        return int_generator()
    elif _type == list or _type == List:
        return list_generator(slices)
    elif _type is None:
        return int_generator()
    else:
        return 'need_to_define_generator'


def str_generator():
    return choice(['random_string', 'ghs dsla ds', '@gmail.com'])


def int_generator():
    return randint(0, 15)


def float_generator():
    return round(random() * 10, 2)


def dict_generator(keys=None):
    _dict = {}
    if keys:
        for key in keys:
            _dict.update({key: map_types(keys[key]['type'])})
    return _dict


def list_generator(slices_):
    """
    :param slices_:
                {0: {'type': <class 'float'>}}
    :return:
    """
    # TODO: can be different types in one list in different indexes
    list_output = []
    if slices_:
        default_elem_type = list(slices_.values())[0]['type']
    else:
        default_elem_type = int
        slices_ = {0: 0}
    for i in range(max(slices_.keys()) + 1):
        if not slices_.get(i):
            elem_type = default_elem_type
        else:
            elem_type = slices_.get(i)['type']
        value = map_types(elem_type)
        list_output.append(value)
    return list_output


def tuple_generator():
    return ()


def set_generator():
    return {}


def obj_generator():
    class Empty:
        pass
    return Empty()
