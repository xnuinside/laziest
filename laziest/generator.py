from collections import defaultdict
from typing import Dict, Text, List
from copy import deepcopy

import laziest.strings as s
from laziest.analyzer import Analyzer
from laziest.random_generators import str_generator


def generate_tests(tree: Dict) -> Text:
    """ main method return tests body/list for one python module """
    test_case = ""

    # signature list need to check diff with existed tests

    for class_ in tree['classes']:
        # define test for non-empty classes function
        if not class_['def'] or isinstance(class_['def'], defaultdict) and not class_['args']:
            print("Empty class")
            continue
        test_case = s.class_signature.format(SP_4=s.SP_4, cls_name=class_['name'])
        for method in class_['def']:
            if method != '__init__':
                test_case += s.class_method_signature.format(SP_4=s.SP_4, method=method)
        for method in class_['async']:
            if method != '__init__':
                test_case += s.class_async_method_signature.format(SP_4=s.SP_4, method=method)

    for funct_name in tree['def']:
        # define test for sync function
        test_case += function_test_creation(funct_name, tree['def'][funct_name])
    for async_funct_name in tree['async']:
        # define test for async function
        test_case += function_test_creation(async_funct_name, tree['async'][async_funct_name],
                                            async_type=True)
    return test_case


def function_test_creation(func_name: Text, func_data: Dict, async_type: bool = False) -> Text:
    """ method to generate test body """
    method_signature = s.method_signature if not async_type else s.async_method_signature
    func_definition = method_signature.format(SP_4=s.SP_4, method=func_name)
    if func_data['args']:
        old_def = func_definition
        func_definition = s.pytest_parametrize_decorator + old_def
        # params structure (1-params values, last 'assert' - assert value)
        null_param = {a: None for a in func_data['args']}
        null_param['assert'] = None
        params = generate_params_based_on_types(null_param, func_data['args'])
        print(params)
        func_definition = func_definition.replace("()", "(params)").replace("[]", str(params))
        args = [a + ", " for a in func_data['args']]
        func_definition += s.assert_string + f" {func_name}({''.join(args)[:-2]})"
        if func_data['return'] is None:
            # check method correct execution
            func_definition += " == None"
    func_definition += "\n\n\n"
    return func_definition


def generate_params_based_on_types(null_param: Dict, args: Dict) -> List:
    params = [null_param]

    print(args)
    default_param = deepcopy(null_param)
    for arg in args:
        if 'default' in args[arg]:
            default_param[arg] = args[arg]['default']
        elif 'type' in args[arg] and not isinstance(args[arg]['type'], dict):
            default_param[arg] = random_generators[map_types(args[arg]['type'])]
    params.append(default_param)
    return params


def map_types(_type):
    if _type == Text or _type == str :
        return 'str'
    else:
        return 'need_to_define'


random_generators = {'str': str_generator(),
                     'need_to_define': 'need_to_define_generator'}


def generate_test_file_content(an: Analyzer) -> Text:
    async_in = True if 'async' in an.tree else False

    file_output = "import pytest\n"

    if async_in:
        file_output = s.async_io_aware_text + file_output

    file_output += "\n\n"
    file_output += generate_tests(an.tree)
    # print(file_output)
