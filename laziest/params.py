from copy import deepcopy
from typing import Dict, List
from random import randint
from laziest.random_generators import str_generator
from laziest.utils import map_types


generators = {'str': str_generator(),
              'need_to_define': 'need_to_define_generator'}

no_default = 'no_default'


def generate_params_based_on_types(null_param: Dict, args: Dict, previous_statements=None, return_pack=None):
    params = deepcopy(null_param)
    print(params)
    if previous_statements and return_pack:
        # we have a functions with ifs
        params = generate_value_in_borders(previous_statements, args, null_param)
        print("STATS")
        print(params)
    else:
        params = gen_params(args, params)
    print(params)
    return params


def gen_params(args, null_param):
    params = deepcopy(null_param)
    for arg in args:
        print(args)
        if 'if' in args[arg]:
            for value in args[arg]['if']:
                new_value = deepcopy(null_param)
                params = [null_param]
                new_value[arg] = value
                params.append(new_value)
                args[arg]['type'] = type(value)

    for arg in args:
        if 'default' in args.get(arg, []):
            params[arg] = args[arg]['default'] \
                if args[arg]['default'] != no_default else randint(0, 7)
        elif 'type' in args[arg] and not isinstance(args[arg]['type'], dict):
            params[arg] = generators[map_types(args[arg]['type'])]
        else:
            params[arg] = randint(0, 7)
    return params


def generate_value_in_borders(previous_statements, args, null_param={}):
    """
    :param previous_statements:
    :param args:
    :return:
    """

    print('previous_statements')
    print(previous_statements)
    print(args)
    final_args = {}
    for arg in args:
        # for each arg check if statements to create value without limits
        args_statements = []
        wrong_values = []
        default_value = 1000
        left_border = -default_value
        right_border = default_value

        for statement in previous_statements:
            if statement['left']['args'] == arg:
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
                        final_args[arg] = val
    if final_args.keys() != args.keys():
        args_with_none = {arg: args[arg] for arg in args if arg not in final_args}
        params = gen_params(args_with_none,
                            {param: null_param[param] for param in null_param if param in args_with_none})
        final_args.update(params)
    return final_args
