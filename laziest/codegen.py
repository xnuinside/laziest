""" Tests body generator """
import os
import re
import traceback
from typing import Dict, Text, Tuple

import laziest.strings as s
import laziest.analyzer as a
from laziest.analyzer import Analyzer
from laziest.asserter import Asserter

reserved_words = ['self', 'cls']


key_import = '$import$'


def generate_tests(tree: Dict, debug: bool):
    """ main method return tests body/list for one python module """
    test_case = ""
    imports = []
    # signature list need to check diff with existed tests
    # method types : class, self, static
    for class_ in tree['classes']:
        # define test for non-empty classes function
        if not class_['def']:
            print("Empty class")
            continue
        method_types = ['self', 'class', 'static']
        for type_ in method_types:
            for method in class_['def'].get(type_, []):
                if method != '__init__':
                    unit_test, func_imports = test_creation(method, class_['def'][type_][method],
                                                            class_=class_, class_method_type=type_, debug=debug)
                    for import_ in func_imports:
                        imports.append(import_)
                    test_case += unit_test
        imports.append(class_['name'])
    for func_name in tree['def']:
        # define test for sync function
        unit_test, func_imports = test_creation(func_name, tree['def'][func_name], debug=debug)
        for import_ in func_imports:
            imports.append(import_)
        test_case += unit_test
        imports.append(func_name)
    return a.pytest_needed, test_case, imports


def add_imports(path):
    imports_header = f'import sys\n' \
                     f'sys.path.append(\'{os.path.dirname(path)}\')\n' \
                     f'from {os.path.basename(path).replace(".py", "")} import {key_import}\n'

    return imports_header


def generate_test_file_content(an: Analyzer, path: Text, debug: bool) -> Text:
    async_in = True if an.tree.get('async') else False
    result = generate_tests(an.tree, debug)
    if result:
        # need to add import of module that we test
        file_output = combine_file(result, path, async_in)
        return file_output


def combine_file(result: tuple, path: Text, async_in: bool) -> Text:
    """
        combine file body
    :param result: result of main generator function
    :param path: path to file, that we test
    :param async_in: exist async in or not, shall we import sync pytest or not
    :return:
    """
    file_output = add_imports(path).replace(key_import, ", ".join(result[2]))
    if async_in:
        file_output = s.async_io_aware_text + file_output
    file_output += "\n\n"
    file_output += result[1]
    file_output = "import pytest\n" + file_output
    return file_output


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
    # if no init args
    class_instance = f'{snake_case_var} = {class_["name"]}()\n'
    if not class_method_type:
        raise
    elif class_method_type not in ['static', 'class', 'self']:
        raise
    if class_method_type == 'static' or class_method_type == 'class':
        func_name = f'{class_["name"]}.{func_name}'
        # we nod need to initialise object
        class_instance = None
    else:
        if '__init__' in class_['def'].get('self'):
            # init_args = class_['def']['self']['__init__']['args']
            # null_param = {a: None for a in class_['def']['self']['__init__']['args']
            # if a not in reserved_words}
            # params = generate_params_based_on_types(null_param, class_)
            # params_line = ', '.join([f'{key}={value}' for key, value in params.items()])
            ...
        func_name = f'{snake_case_var}.{func_name}'
    return class_instance, func_name


def test_body_resolver(test_func_definition: Text, func_name: Text, func_data: Dict,
                       class_=None, class_method_type=None):
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
    :param test_func_definition:
    :param func_name:
    :param func_data:
    :param class_:
    :param class_method_type:
    :return:
    """
    instance_ = None
    class_instance = None
    if class_:
        class_instance, func_name = class_methods_names_create(func_name, class_, class_method_type)
    if not instance_:
        function_header_init = s.assert_string
    else:
        function_header_init = instance_ + "\n" + s.SP_4 + s.assert_string
    if class_instance:
        test_func_definition += class_instance
    asserts_definition = set()
    imports = []
    log = False
    # init asserter
    asserter = Asserter(func_data)
    # get returns result per args group
    returns_ = asserter.return_assert_values()

    for args, return_value, err_message, log_, random_values in returns_:
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
                    print(arg, value)
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
    for assert_ in asserts_definition:
        test_func_definition += f"\n{s.SP_4}" + assert_
    return test_func_definition, log, imports


def test_creation(func_name: Text, func_data: Dict, debug: bool,
                  class_=None, class_method_type=None) -> Tuple[Text, Text]:
    """ method to generate test body """
    imports = []
    if class_:
        func_definition = get_method_signature(func_name, func_data['async_f'], class_['name'])
    else:
        metod_signature = get_method_signature(func_name, func_data['async_f'])
        func_definition = metod_signature
    if isinstance(func_data, dict) and 'error' not in func_data:
        try:
            func_definition, log, imports = test_body_resolver(
                func_definition, func_name, func_data, class_, class_method_type)
            func_definition += "\n\n\n"
            if log:
                method_signature_with_capture = metod_signature.replace('()', '(capsys)')
                func_definition = func_definition.replace(metod_signature, method_signature_with_capture)
        except Exception as e:
            if debug:
                trace = "".join([f'\n{s.SP_4}#{line}' for line in traceback.format_exc(1).split('\n')])
                func_definition += f'\n{s.SP_4}# {e}\n{trace}\n{s.SP_4}pass\n'
            else:
                raise e
    else:
        func_definition += f'\n{s.SP_4}# {func_data["comment"]}\n{s.SP_4}pass\n'
    return func_definition, imports
