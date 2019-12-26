from typing import Dict, Text
from laziest.params import generate_params_based_on_types
from laziest import strings as s
from copy import deepcopy
from laziest import analyzer


normal_types = [int, str, list, dict, tuple, set, bytearray, bytes]


def get_method_signature(func_name: Text, async_type: bool, class_name=None) -> Text:
    if class_name:
        func_name = f'{convert(class_name)}_{func_name}'
    method_signature = s.method_signature if not async_type else s.async_method_signature
    # create test method signature
    func_definition = method_signature.format(SP_4=s.SP_4, method=func_name)
    return func_definition


def eval_binop_with_params(bin_op, global_params, params):
    print(bin_op)
    print(global_params)
    global_params.update(params)
    print(params)
    try:
        return_value = eval(bin_op, global_params)
    except Exception as e:
        analyzer.pytest_needed = True
        return_value = {'error': (e.__class__, e,)}
    return return_value


def get_assert_for_params(func_data, params):
    if isinstance(func_data['return'], tuple):
        return_value = []
        for num, _ in enumerate(func_data['return']):
            if 'arg' in func_data['return'][num]:
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
    return return_value

import re


def convert(name):
    """ from camel case / pascal case to snake_case
    :param name:
    :return:
    """
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def test_body_resolver(func_definition: Text, func_name: Text, func_data: Dict,
                       class_=None, class_method_type=None) -> Text:
    print(func_data)
    instance_ = None

    reserved_name = ['self', 'cls']
    if class_:
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
                print('init 1')
                print(init_args)
                null_param = {a: None for a in class_['def']['self']['__init__']['args']
                              if a not in reserved_name}
                filtered_args = {x: init_args[x] for x in init_args
                                 if x not in reserved_name}
                print(filtered_args)
                params = generate_params_based_on_types(null_param, filtered_args)
                params_line = ', '.join([f'{key}={value}' for key, value in params.items()])
                instance_ = f'{snake_case_var}  = {class_["name"]}({params_line})'
            func_name = f'{snake_case_var}.{func_name}'
    print(func_data)
    if func_data['args']:
        # func_definition = s.pytest_parametrize_decorator + func_definition
        # params structure (1-params values, last 'assert' - assert value)
        null_param = {a: None for a in func_data['args']}
        if class_method_type != 'static':
            func_data['args'] = {x: func_data['args'][x] for x in deepcopy(null_param)
                                 if x not in reserved_name}
            null_param = {x: null_param[x]
                          for x in null_param if x not in reserved_name}
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
        print(params)
        functions_headers = []
        for param in params:
            params_line = ', '.join([f'{key} = {value}' if not isinstance(
                value, str) else f'{key} = \"{value}\"' for key, value in param.items()])
            function_header_per_args = function_header + f' {func_name}({params_line})'
            functions_headers.append(function_header_per_args)

    eq_line = " is " if func_data['return'] is None else f" == "
    if isinstance(func_data['return'], dict):
        if 'error' in func_data['return']:
            # if we have exception
            print(str(func_data['return']['error'][0]))
            exc_name = str(func_data['return']['error'][0]).split('\'')[1]
            comment = f'{s.SP_4}{s.SP_4}# ' + str(func_data['return']['error'][1])
            func_definition += f" with pytest.raises({exc_name}): \n{comment} \n" \
                               f"{s.SP_4}{s.SP_4}{func_name}()"
    elif func_data['args']:
        print('me here')
        for function in functions_headers:
            func_definition += function + f"{eq_line}{params_assert}" + f"\n{s.SP_4}"
    else:
        func_definition += function_header + eq_line + (f"\'{func_data['return']}\'" if isinstance(
            func_data['return'], str) else f"{func_data['return']}")
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
