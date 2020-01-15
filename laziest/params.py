from copy import deepcopy
from typing import Dict, List
from random import randint
from laziest.random_generators import str_generator
from laziest.utils import map_types
from laziest.analyzer import no_default


generators = {'str': str_generator(),
              'need_to_define': 'need_to_define_generator'}


def generate_params_based_on_types(null_param: Dict, args: Dict):

    params = deepcopy(null_param)

    print('params')
    print(params)
    for arg in args:
        if 'if' in args[arg]:
            # 'if': {'values': ['1'], 'return': [{'error': 'Exception'}]}})]),
            # 'kargs_def': [], 'kargs': None, 'return': None}
            for num, value in enumerate(args[arg]['if']['values']):
                if not params[arg]:
                    params[arg] = []

                params[arg].append({value: args[arg]['if']['return'][num]})
                args[arg]['type'] = type(value)

    for arg in args:
        print(args)
        if 'default' in args.get(arg, []):
            params[arg] = args[arg]['default'] \
                if args[arg]['default'] != no_default else randint(0, 7)
        elif 'type' in args[arg] and not isinstance(args[arg]['type'], dict):
            params[arg] = generators[map_types(args[arg]['type'])]
        else:
            params[arg] = randint(0, 7)
    params = tuple(params)
    print('hello')
    print(params)
    return params
