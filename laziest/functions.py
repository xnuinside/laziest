from typing import Dict, Text
from laziest import strings as s
import re
from copy import deepcopy
from laziest import analyzer
from laziest.params import generate_params_based_on_types
from laziest.asserter import return_assert_value

reserved_words = ['self', 'cls']

normal_types = [int, str, list, dict, tuple, set, bytearray, bytes]


def get_method_signature(func_name: Text, async_type: bool, class_name=None) -> Text:
    if class_name:
        func_name = f'{convert(class_name)}_{func_name}'
    method_signature = s.method_signature if not async_type else s.async_method_signature
    # create test method signature
    func_definition = method_signature.format(SP_4=s.SP_4, method=func_name)
    return func_definition


def eval_binop_with_params(bin_op, global_params, params):
    """
        eval binop with params to get result
    :param bin_op:
    :param global_params:
    :param params:
    :return:
    """
    global_params.update(params)
    try:
        return_value = eval(bin_op, global_params)
    except Exception as e:
        analyzer.pytest_needed = True
        return_value = {'error': (e.__class__, e,)}
    return return_value


def get_assert_for_params(func_data, params):
    print('we params')
    print(params)
    if isinstance(func_data['return'], tuple):
        return_value = []
        for num, _ in enumerate(func_data['return']):
            if 'arg' in func_data['return'][num]:
                print(func_data['return'])
                print('returnnn')
                return_value.append(params[func_data['return'][num]['arg']])
            elif 'BinOp' in func_data['return'][num]:
                result = eval_binop_with_params(
                    func_data['return'][num]['BinOp'],
                    func_data['return'][num].get('global_vars', {}),
                    params)
                if isinstance(result, dict) and 'error' in result:
                    return_value = result
                    break
                else:
                    return_value.append(result)
            elif type(func_data['return'][num] in normal_types):
                return_value.append(func_data['return'][num])
        if isinstance(return_value, list):
            return_value = tuple(return_value)
    elif isinstance(func_data['return'], dict) and 'BinOp' in func_data['return']:
        return_value = eval_binop_with_params(func_data['return']['BinOp'], func_data['return'].get(
            'global_vars', {}), params)
    elif isinstance(func_data['return'], dict) and 'arg' in func_data['return']:
        return_value = params[func_data['return']['arg']]
    elif func_data['return'] is None:
        return_value = None
    else:
        print('return')
        print(func_data)
        print(func_data['return'])
        raise Exception(func_data['return'])
    print('return_value')
    print(return_value)
    print(func_data)
    return {'args': params, 'result': return_value}


def convert(name):
    """ from camel case / pascal case to snake_case
    :param name:
    :return:
    """
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def class_methods_names_create(func_name, class_, class_method_type):

    snake_case_var = convert(class_["name"])
    if not class_method_type:
        raise
    elif class_method_type not in ['static', 'class', 'self']:
        raise
    if class_method_type == 'static' or class_method_type == 'class':
        func_name = f'{class_["name"]}.{func_name}'
    else:
        if '__init__' in class_['def'].get('self'):
            init_args = class_['def']['self']['__init__']['args']
            null_param = {a: None for a in class_['def']['self']['__init__']['args']
                          if a not in reserved_words}
            filtered_args = {x: init_args[x] for x in init_args
                             if x not in reserved_words}
            params = generate_params_based_on_types(null_param, filtered_args)
            params_line = ', '.join([f'{key}={value}' for key, value in params.items()])
            instance_ = f'{snake_case_var}  = {class_["name"]}({params_line})'
        func_name = f'{snake_case_var}.{func_name}'
    return func_name


def test_body_resolver(func_definition: Text, func_name: Text, func_data: Dict,
                       class_=None, class_method_type=None) -> Text:
    """
        func_data format:
             {.. 'def': {'function': {'args': OrderedDict(),
                      'kargs': None,
                      'kargs_def': [],
                      'return': None},
         'function_with_constant_return_float': {'args': OrderedDict(),
                                                 'kargs': None,
                                                 'kargs_def': [],
                                                 'return': 1.003} ...}
        {.. 'def': {'function': {'args': OrderedDict(),
                      'kargs': None,
                      'kargs_def': [],
                      'return': None},
         'function_with_constant_return_float': {'args': OrderedDict(arg1, arg2, arg3),
                                                 'kargs': None,
                                                 'kargs_def': [],
                                                 'return': 1.003} ...}
         'return': [{args: {arg1: , arg2: , arg3 }, result: }]
    :param func_definition:
    :param func_name:
    :param func_data:
    :param class_:
    :param class_method_type:
    :return:
    """
    print(func_data)
    # raise
    instance_ = None

    if class_:
        func_name = class_methods_names_create(func_name, class_, class_method_type)
    if func_data['args']:
        # func_definition = s.pytest_parametrize_decorator + func_definition
        # params structure (1-params values, last 'assert' - assert value)
        null_param = {a: None for a in func_data['args']}
        if class_method_type != 'static':
            func_data['args'] = {x: func_data['args'][x] for x in deepcopy(null_param)
                                 if x not in reserved_words}
            null_param = {x: null_param[x]
                          for x in null_param if x not in reserved_words}
        params = generate_params_based_on_types(null_param, func_data['args'])
        params_assert = get_assert_for_params(func_data, params)
        func_data['return'] = params_assert
    if not instance_:
        function_header = s.assert_string
    else:
        function_header = instance_ + "\n" + s.SP_4 + s.assert_string
    if not func_data['args']:
        function_header += f' {func_name}()'
    else:
        functions_headers = []
        print(params)
        params_line = ', '.join([f'{key} = {value}' if not isinstance(
            value, str) else f'{key} = \"{value}\"' for key, value in params.items()])
        function_header_per_args = function_header + f' {func_name}({params_line})'
        functions_headers.append(function_header_per_args)

    asserts_definition = []
    for args, return_value, comment in return_assert_value(func_data):
        if comment:
            # mean we have an error rise
            asserts_definition_str = f" with pytest.raises({return_value}): \n# {comment} \n" \
                               f"{s.SP_4}{s.SP_4}{func_name}()"
        else:
            eq_line = " is " if return_value is None else f" == "
            return_value = str(return_value) if not isinstance(return_value, str) else f"\'{return_value}\'"
            asserts_definition_str = func_name + '()' + f"{eq_line}" + return_value + f"\n{s.SP_4}"
        asserts_definition.append(asserts_definition_str)
    for assert_ in asserts_definition:
        func_definition += f"\n{s.SP_4}" + assert_
    return func_definition


def test_creation(func_name: Text, func_data: Dict, async_type: bool = False,
                  class_=None, class_method_type=None) -> Text:
    """ method to generate test body """
    if class_:
        func_definition = get_method_signature(func_name, async_type, class_['name'])
    else:
        func_definition = get_method_signature(func_name, async_type)
    func_definition = test_body_resolver(func_definition, func_name, func_data, class_, class_method_type)
    func_definition += "\n\n\n"
    return func_definition


