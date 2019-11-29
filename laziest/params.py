from copy import deepcopy
from typing import Dict, List
from laziest.random_generators import str_generator
from laziest.utils import map_types


generators = {'str': str_generator(),
                     'need_to_define': 'need_to_define_generator'}



def generate_params_based_on_types(null_param: Dict, args: Dict) -> List:
    params = [null_param]

    print(args)
    default_param = deepcopy(null_param)
    for arg in args:
        if 'default' in args[arg]:
            default_param[arg] = args[arg]['default']
        elif 'type' in args[arg] and not isinstance(args[arg]['type'], dict):
            default_param[arg] = generators[map_types(args[arg]['type'])]
    params.append(default_param)
    return params
