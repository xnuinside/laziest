from copy import deepcopy
from typing import Dict, Any, Union, List, Text
from random import randint
from collections import defaultdict
from collections.abc import Iterable
# TODO: temporary, after need to integrate with hypothesis or smth else to generate valuse
from laziest.argsgen import map_types, map_types_in_range, map_types_include
from laziest.utils import get_value_name, is_int
no_default = 'no_default'

cls_reserved_args = ['self', 'cls']


def generate_params_based_on_strategy(args: Dict, func_data: Dict, strategies=None, base_params=None):
    if strategies and base_params:
        # we have a functions with ifs
        params = generate_value_in_borders(strategies, args, base_params, func_data)
    else:
        params = deepcopy(args)
        params = gen_params(func_data['args'], func_data['keys'], params)
    return params


def gen_params(args, keys, null_param):
    params = deepcopy(null_param)
    depended_args, filterred_args = [], []

    for arg in args:
        if arg not in cls_reserved_args:
            if 'depend_on' in args[arg]:
                depended_args.append(arg)
            else:
                filterred_args.append(arg)

    for arg in filterred_args:
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
    for arg in depended_args:
        depend_on_arg = params[args[arg]['depend_on']]
        if isinstance(depend_on_arg, str):
            params[arg] = depend_on_arg[int(len(depend_on_arg)/3):len(depend_on_arg)-1]
    return params


def add_border_to_arg(args_borders: Dict, arg_name: Text, value: Any, border: Text, _slice=None):
    """
        args_borders = {arg: {
                            exclude: [],
                            left: [4]},
                            right: [5]},
                            4: 1}
                            },
                        arg2: { slices: {
                                'normal': {
                                },
                                exclude: []
                            }

                        }

    :param args_borders:
    :param arg_name:
    :param value:
    :param border:
    :param _slice:

    :return:
    TODO: need correct work with paired statements like
        arg1 < 5 and arg1 > 2 or arg1 > 7 and arg1 < 12
            must be pairs like (2,5) and (7,12)
        need to add changes to strategies also
    """
    if not args_borders.get(arg_name):
        args_borders[arg_name] = {'left': [], 'right': [], 'exclude': [], 'include': []}

        if _slice:
            args_borders[arg_name]['slice'] = defaultdict(dict)
            if not args_borders[arg_name]['slice'].get(_slice):
                args_borders[arg_name]['slice'][_slice] = defaultdict(list)
    if _slice:
        args_borders[arg_name]['slice'][_slice][border].append(value)
    else:
        args_borders[arg_name][border].append(value)
    return args_borders


def set_slice_value(_object: Union[Iterable, List, Dict], _slice: Union[int, str], value: Any) -> Iterable:
    int_slice = is_int(_slice)
    if int_slice:
        if len(_object) > int_slice:
            _object[int_slice] = value
        else:
            print('For some reason in set_slice_value object with slice comes with lenght < _slice index')
            while len(_object) > int_slice:
                _object.append(value)
    else:
        _object[_slice] = value
    return _object


def get_side_of_argument(statement: Dict) -> Text:
    _statement = deepcopy(statement)
    for side in ['left', 'comparators']:
        if isinstance(_statement.get(side, None), Iterable):
            if 'arg' in _statement[side]:
                _statement[side] = _statement[side]['arg']
            if 'args' in _statement[side]:
                # TODO: need to work around correct case when one arg compared to another
                return side


def get_border_from_statement(args, statement, args_borders):
    sides = {
        '>': 'left',
        '<': 'right',
        '!=': 'exclude',
        '<=': 'right',  # TODO: need also include an edge value, same for >=
        '>=': 'left',
        'in': 'include',
        'not in': 'exclude'
    }

    opposite_side = {
        'left': 'comparators',
        'comparators': 'left'
    }
    arg_side = get_side_of_argument(statement)
    _arg_name, _slice = get_value_name(statement[arg_side], separate_slice=True)
    if statement.get('ops') == '==':
        if not _slice:
            args[_arg_name] = statement[opposite_side[arg_side]]
        else:
            args[_arg_name] = set_slice_value(args[_arg_name], _slice, statement[opposite_side[arg_side]])

    else:
        operator = sides[statement['ops']]
        border_value_key = statement[opposite_side[arg_side]]
        if not statement.get('ops'):
            # mean value must exist, no matter that int != 0, str != '' and etc
            if not _slice:
                args[_arg_name] = statement[opposite_side[arg_side]]
            else:
                args[_arg_name] = set_slice_value(args[_arg_name], _slice,
                                                  statement[opposite_side[arg_side]])

        if not _slice:

            args_borders = add_border_to_arg(args_borders, _arg_name, border_value_key,
                                             operator)
        else:
            args_borders = add_border_to_arg(args_borders, _arg_name, statement[opposite_side[arg_side]],
                                             operator, _slice=_slice)
    return args_borders


def extract_border_values(strategies, args):
    args_borders = {}
    for statement_group in strategies:
        if isinstance(statement_group, list):
            for statement in statement_group:
                args_borders = get_border_from_statement(args, statement, args_borders)
        else:
            args_borders = get_border_from_statement(args, statement_group, args_borders)
    return args_borders


def create_value_in_border_per_arg(arg_type: Any, arg_borders: Dict, _slice=False) -> Any:
    """
        arg_borders = {'left_border': ,
                        'right_borders': ,
                        'exclude': ..}
    :param arg_type:
    :param arg_borders:
    :return:
    """
    default_value = 1000
    # TODO: fix work with multiple ranges, now just 0 index
    if arg_borders['left']:
        left_border = arg_borders['left'][0] + 1
    else:
        left_border = -default_value
    if arg_borders['right']:
        right_border = arg_borders['right'][0]
    else:
        right_border = default_value
    exclude = arg_borders['exclude']
    include = arg_borders['include']
    if _slice:
        arg_type = int
    if left_border != -default_value or right_border != default_value:
        # we have int or float
        value = None
        n = 0
        while not value and n != 3:
            values = map_types_in_range(arg_type, left_border, right_border)
            for val in values:
                if exclude:
                    for ex_val in exclude:
                        if val != ex_val:
                            return val
                else:
                    return val
            else:
                n += 1

    elif exclude or include:
        return map_types_include(arg_type, include, exclude)
    else:
        raise


def prepare_args(args):
    # TODO: need remove possible to arrive arg names with slice like 'arg2[3]' and after reduce this function
    del_keys = []
    for arg in args:
        if '[' in arg:
            _arg_name = arg.split('[')[0]
            _slice = arg.split('[')[1].split(']')[0]
            if _arg_name in args:
                int_slice = is_int(_slice)
                if int_slice:
                    args[_arg_name][int_slice] = deepcopy(args[arg])
                else:
                    args[_arg_name][_slice] = deepcopy(args[arg])

            else:
                raise Exception(arg, args, 'prepare_args')
            del_keys.append(arg)
    for key in del_keys:
        del args[key]
    return args


def generate_value_in_borders(strategies: List, args: Dict, base_params: Dict, func_data: Dict):
    """
        generate values if exist previous borders (statemnts) from 'ifs'
    :param strategies:
    :param args:
    :param base_params:
    :return:
    """
    if base_params is None:
        base_params = {}
    # borders from strategies
    for arg in base_params:
        if arg not in args:
            args[arg] = base_params[arg]
    args = prepare_args(args)
    args_borders = extract_border_values(strategies, args)
    for arg in args_borders:
        if 'slice' in args_borders[arg]:
            for slice_ in args_borders[arg]['slice']:
                _value = create_value_in_border_per_arg(
                    func_data['args'][arg]['type'], args_borders[arg]['slice'][slice_], _slice=True)
                set_slice_value(args[arg], slice_, _value)
        else:
            _value = create_value_in_border_per_arg(func_data['args'][arg]['type'], args_borders[arg])
            args[arg] = _value
    return args
