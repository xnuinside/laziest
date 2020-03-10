# TODO: temporary, after need to integrate with hypothesis or smth else to generate values
from typing import Dict, Text, List, Union
from random import random, randint, choice


def map_types_in_range(_type, left_border: int, right_border: int, _slice: Union[int, Text] = None):
    if _slice:
        return int_generator(left_border, right_border)
    if _type == {'No type': True} or _type == int:
        return int_generator(left_border, right_border)
    elif _type == float:
        return float_generator(left_border, right_border)
    elif _type == Text or _type == str:
        return str_generator()
    else:
        return f'need_to_define_generator_for_type_{_type}_in_range'


def map_types_include(_type, include=None, exclude=None, slices=None):
    if _type == Text or _type == str:
        return str_generator(include, exclude)
    elif _type == float:
        return float_generator(include=include, exclude=exclude)
    else:
        return f'need_to_define_generator_for_type_{_type}_include'


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


def str_generator(include=None, exclude=None):
    _str = choice(['random_string', 'ghs dsla ds', '@gmail.com'])
    if include:
        index = randint(0, 5)
        _str = _str[:index] + " ".join(include) + _str[index:]
    elif exclude:
        if isinstance(exclude, list):
            for elem in exclude:
                _str = _str.replace(elem, '')
    return _str


def int_generator(left_border=None, right_border=None):
    if left_border and right_border:
        return [randint(left_border, right_border) for _ in range(0, 3)]
    return randint(1, 15)


def float_generator(left_border: int = None, right_border: int = None, include=None, exclude=None):
    if include:
        return include
    if exclude:
        return [x for x in [round(random() * 10, 2) for _ in range(0, 3)] if x not in exclude][0]
    if left_border and right_border:
        return [round(randint(left_border, right_border) * random() * 10, 2) for _ in range(0, 3)]
    else:
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
