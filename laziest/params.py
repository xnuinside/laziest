from copy import deepcopy
from typing import Dict, List
from random import randint
from laziest.random_generators import str_generator
from laziest.utils import map_types


generators = {'str': str_generator(),
              'need_to_define': 'need_to_define_generator'}


def generate_params_based_on_types(null_param: Dict, args: Dict):

    default_param = deepcopy(null_param)
    for arg in args:
        if 'if' in args[arg]:
            for value in args[arg]['if']:
                new_value = deepcopy(default_param)
                default_param = [default_param]
                new_value[arg] = value
                default_param.append(new_value)
                args[arg]['type'] = type(value)

    for arg in args:
        print(args)
        if 'default' in args.get(arg, []):
            default_param[arg] = args[arg]['default']
        elif 'type' in args[arg] and not isinstance(args[arg]['type'], dict):
            default_param[arg] = generators[map_types(args[arg]['type'])]
        else:
            default_param[arg] = randint(0, 7)
    print('hello')
    print(default_param)
    return default_param
