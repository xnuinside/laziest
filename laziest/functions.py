from typing import Dict, Text, Tuple
from laziest import strings as s
import re
# from laziest.params import generate_params_based_on_types
from laziest.asserter import return_assert_value

reserved_words = ['self', 'cls']


def get_method_signature(func_name: Text, async_type: bool, class_name=None) -> Text:
    if class_name:
        func_name = f'{convert(class_name)}_{func_name}'
    method_signature = s.method_signature if not async_type else s.async_method_signature
    # create test method signature
    func_definition = method_signature.format(SP_4=s.SP_4, method=func_name)
    return func_definition


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
            # init_args = class_['def']['self']['__init__']['args']
            # null_param = {a: None for a in class_['def']['self']['__init__']['args']
            # if a not in reserved_words}
            # params = generate_params_based_on_types(null_param, class_)
            # params_line = ', '.join([f'{key}={value}' for key, value in params.items()])
            ...
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
    instance_ = None

    if class_:
        func_name = class_methods_names_create(func_name, class_, class_method_type)
    if not instance_:
        function_header_init = s.assert_string
    else:
        function_header_init = instance_ + "\n" + s.SP_4 + s.assert_string

    asserts_definition = set()
    imports = []
    log = False
    returns_ = return_assert_value(func_data)
    for args, return_value, err_message, log_, random_values in returns_:
        print('return_value')
        print(return_value)
        await_prefix = '( await ' if func_data['async_f'] else ''
        # form text functions bodies based on args, return_values and comments
        if log_:
            function_header = await_prefix + f'{func_name}'
        else:
            function_header = function_header_init + ' ' + await_prefix + f'{func_name}'
        if not args:
            function_header += '()'
        else:
            params_line = ', '.join([f'{key}={value}' if not isinstance(
                value, str) else f'{key}=\"{value}\"' for key, value in args.items()])
            function_header += f'({params_line})'
            if await_prefix:
                function_header += ')'
        if err_message:
            # mean we have an error raise
            if return_value not in globals()['__builtins__']:
                # if not standard error
                imports.append(return_value)
            asserts_definition_str = f"with pytest.raises({return_value}): \n{s.SP_4}{s.SP_4}" \
                                     f"#  error message: {err_message} \n" \
                                     f"{s.SP_4}{s.SP_4}{function_header}"
        elif log_:
            log = True

            def _get_str_value():
                for arg, value in args.items():
                    locals()[arg] = value
                str_ = f"\'{eval(return_value)}\\n\'"
                return str_
            asserts_definition_str = function_header + f"\n{s.SP_4}" \
                                                       f"" + s.log_capsys_str + f"\n{s.SP_4}assert captured.out " \
                                                                                f"== {_get_str_value()}\n"
        elif random_values:
            # this mean we have dict, but some result can be generated randomly in runtime
            # we create several asserts per key without random and assert is not None to random key
            for key in return_value:
                print(return_value[key])
                value = str(return_value[key]) if not isinstance(return_value[key], str) else f'\'{return_value[key]}\''
                if key not in random_values:
                    asserts_definition_str = function_header + f'[\'{key}\']' + " == " \
                                             + value + f"\n{s.SP_4}"
                else:
                    asserts_definition_str = function_header + f'[\'{key}\']' + " is not None "
                asserts_definition.add(asserts_definition_str)
        else:
            eq_line = " is " if return_value is None else f" == "

            return_value = str(return_value) if not isinstance(return_value, str) else f"\'{return_value}\'"
            asserts_definition_str = function_header + f"{eq_line}" + return_value + f"\n{s.SP_4}"
        asserts_definition.add(asserts_definition_str)
    print('asserts_definition')
    print(asserts_definition)
    for assert_ in asserts_definition:
        func_definition += f"\n{s.SP_4}" + assert_
    return func_definition, log, imports


def test_creation(func_name: Text, func_data: Dict,
                  class_=None, class_method_type=None) -> Tuple[Text, Text]:
    """ method to generate test body """
    if class_:
        func_definition = get_method_signature(func_name, func_data['async_f'], class_['name'])
    else:
        metod_signature = get_method_signature(func_name, func_data['async_f'])
        func_definition = metod_signature
    func_definition, log, imports = test_body_resolver(func_definition, func_name, func_data, class_, class_method_type)
    func_definition += "\n\n\n"
    if log:
        method_signature_with_capture = metod_signature.replace('()', '(capsys)')
        func_definition = func_definition.replace(metod_signature, method_signature_with_capture)
    return func_definition, imports
