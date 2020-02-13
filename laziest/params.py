from copy import deepcopy
from typing import Dict
from random import randint
# TODO: temporary, after need to integrate with hypothesis or smth else to generate valuse
from laziest.random_generators import map_types

no_default = 'no_default'


def generate_params_based_on_types(null_param: Dict, func_data: Dict, previous_statements=None, return_pack=None):
    params = deepcopy(null_param)
    print(params)
    if previous_statements and return_pack:
        # we have a functions with ifs
        params = generate_value_in_borders(previous_statements, func_data, null_param)
    else:
        params = gen_params(func_data['args'], func_data['keys'], params)
    return params


def gen_params(args, keys, null_param):
    params = deepcopy(null_param)
    print(params)
    print(args)
    for arg in args:
        if 'if' in args[arg]:
            for value in args[arg]['if']:
                new_value = deepcopy(null_param)
                params = [null_param]
                new_value[arg] = value
                params.append(new_value)
                args[arg]['type'] = type(value)

        elif 'default' in args.get(arg, []):
            params[arg] = args[arg]['default'] \
                if args[arg]['default'] != no_default else randint(0, 7)
        elif 'type' in args[arg] and not isinstance(args[arg]['type'], dict):
            _slices = {}
            if keys:
                for key in keys:
                    if arg in keys[key]:
                        _slices[key] = {'type': keys[key][arg]['type']}
            params[arg] = map_types(args[arg]['type'], slices=_slices)
        else:
            params[arg] = randint(0, 7)
    return params


def generate_value_in_borders(previous_statements, func_data, null_param=None):
    """
        generate values if exist previous borders (statemnts) from 'ifs'
    :param previous_statements:
    :param func_data:
    :param null_param:
    :return:
    """

    final_args = {}
    if not null_param:
        null_param = None
    for arg in func_data['args']:
        wrong_values = []
        default_value = 1000
        left_border = -default_value
        right_border = default_value
        _slice = None
        for statement in previous_statements:
            print(statement)
            if 'arg' in statement['left']:
                args = statement['left']['arg']['args']
                _slice = statement['left']['slice']
            else:
                args = statement['left']['args']
            if args == arg:
                if statement['ops'] == '==':
                    wrong_values.append(statement['comparators'])
                elif statement['ops'] == '>':
                    right_border = statement['comparators'] - 1
                elif statement['ops'] == '<':
                    left_border = statement['comparators'] + 1
        if left_border != (-default_value) or right_border != default_value:
            # we have int
            generate_values = [randint(left_border, right_border) for _ in range(0, 3)]

            for val in generate_values:
                for wr_val in wrong_values:
                    if val != wr_val:
                        if not _slice:
                            final_args[arg] = val
                        else:
                            _type = dict if isinstance(_slice, str) else list
                            _arg = map_types(_type=_type, slices=_slice)
                            _arg[_slice] = val
                            final_args[arg] = _arg
    if final_args.keys() != func_data['args'].keys():
        args_with_none = {arg: func_data['args'][arg] for arg in func_data['args'] if arg not in final_args}
        params = gen_params(args_with_none, func_data['keys'],
                            {param: null_param[param] for param in null_param if param in args_with_none})
        final_args.update(params)
    print('final_args')
    print(final_args)
    return final_args
