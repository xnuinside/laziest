""" Tests body generator """
import os
from typing import Dict, Text

import laziest.strings as s
from laziest.analyzer import Analyzer
from laziest import functions as f
import laziest.analyzer as a


def generate_tests(tree: Dict):
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
                    test_case += f.test_creation(method, class_['def'][type_][method],
                                                 class_=class_, class_method_type=type_)
        imports.append(class_['name'])
    for func_name in tree['def']:
        # define test for sync function
        unit_test, funct_imports = f.test_creation(func_name, tree['def'][func_name])
        for import_ in funct_imports:
            imports.append(import_)
        test_case += unit_test
        imports.append(func_name)
    for async_funct_name in tree['async']:
        # define test for async function
        test_case += f.test_creation(async_funct_name,
                                     tree['async'][async_funct_name])
    return a.pytest_needed, test_case, imports


key_import = '$import$'


def add_imports(path):
    imports_header = f'import sys\n' \
                     f'sys.path.append(\'{os.path.dirname(path)}\')\n' \
                     f'from {os.path.basename(path).replace(".py", "")} import {key_import}\n'

    return imports_header


def generate_test_file_content(an: Analyzer, path: Text) -> Text:
    async_in = True if an.tree.get('async') else False
    result = generate_tests(an.tree)
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
