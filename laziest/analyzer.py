""" result of analyzers work - data from ast that needed to asserter """
import ast
import _ast

from copy import deepcopy
from typing import Any, Text, Dict
from pprint import pprint
from collections import defaultdict, OrderedDict
from laziest import ast_meta as meta
from laziest.params import generate_value_in_borders
from random import randint

pytest_needed = False

bin_ops = ['+', '-', '*', '/', '', '%', '//']


class Analyzer(ast.NodeVisitor):
    """ class to parse files in dict structure to provide to generator data,
    that needed for tests generation """

    def __init__(self, source: Text):
        """
            source - code massive
        :param source:
        """
        self.tree = {"import": [],
                     "from": [],
                     "def": {},
                     "raises": [],
                     "classes": [],
                     "async": {}}
        # list of source lines
        self.source = source.split("\n")
        self.func_data = {}
        self.variables = []
        self.variables_names = []

    def visit_Import(self, node):
        for alias in node.names:
            self.tree["import"].append(alias.name)
        self.generic_visit(node)

    def visit_FromImport(self, node):
        for alias in node.names:
            self.tree["from"].append(alias.name)
        self.generic_visit(node)

    def process_if_construction(self, statement, func_data, variables_names, variables, previous_statements=None):
        if previous_statements is None:
            previous_statements = []
        # we get variables from statement
        value = self.get_value(statement.test, variables_names, variables)
        # we work with args from statements
        args = {}
        previous_statements.append(value)
        if value['ops'] == '==':
            args = {value['left']['args']: value['comparators']}
        elif value['ops'] == '>':
            args = {value['left']['args']: value['comparators'] + randint(1, 100)}
        result = self.get_value(statement.body[0])
        index = len(func_data['return'])
        print(statement.body[0].__dict__)
        if 'print' in result:
            print(result)
            result = result['print']['text'].replace('    ', '')
        func_data['return'].append({'args': args, 'result': result})
        func_data['return'][index]['log'] = True
        for orelse in statement.orelse:
            if isinstance(orelse, _ast.If):
                func_data = self.process_if_construction(
                    orelse, func_data, variables_names, variables, previous_statements)
            elif isinstance(orelse, ast.Return):
                func_data['return'].append(self.generate_arg_based_on_previous_conditions(
                    orelse.value, func_data, previous_statements))
        func_data['ifs'] = previous_statements
        return func_data

    def generate_arg_based_on_previous_conditions(self, return_node, func_data, previous_statements):
        return_value = self.get_value(return_node)
        print(return_value)
        print('generate_result_based_on_previous_conditions')
        if 'args' in return_value:
            _value = generate_value_in_borders(previous_statements, func_data, {return_value['args']: None})
            print(_value)
            return {'args': _value, 'result': return_value}

    def extract_variables_in_scope(self, node):
        """
            method to extract variables and variables names, that used in scope
        :param node:
        :return:
        """
        # local variables, assign statements in function body
        variables = [node for node in node.body if isinstance(node, ast.Assign)]
        variables_names = {}
        if variables:
            # define code variables in dict
            for index, var in enumerate(variables):
                var_names = {name_node.id: index for name_node in var.targets}
                variables_names.update(var_names)
        self.variables = variables
        self.variables_names = deepcopy(variables_names)
        self.func_data['variables'] = self.variables
        return variables, variables_names

    def function_data_base(self, node, async_f):
        """
            define base for collection function_data
        :param node:
        :param async_f:
        :return:
        """
        self.func_data = {'args': self.get_function_args(node),
                          'kargs_def': node.args.kw_defaults,
                          'kargs': node.args.kwarg,
                          'return': [],
                          'async_f': async_f,
                          'keys': defaultdict(dict),
                          'variables': []}
        return self.func_data

    def visit_FunctionDef(self, node, async_f=False, class_=None):
        """ main methods to """
        func_data = self.function_data_base(node, async_f)
        variables, variables_names = self.extract_variables_in_scope(node)
        non_variables_nodes_bodies = [node for node in node.body if node not in variables]
        for body_item in non_variables_nodes_bodies:
            if isinstance(body_item, ast.Return):
                return_ = {'result': self.get_value(body_item.value, variables_names, variables)}
                func_data['return'].append(return_)
            if isinstance(body_item, _ast.If):
                func_data = self.process_if_construction(
                    body_item, self.func_data, variables_names, variables)
        if not class_:
            self.tree['def'][node.name] = deepcopy(func_data)

        if not func_data['return']:
            # if function does not return anything
            func_data['return'] = [{'args': (), 'result': None}]
        return func_data

    def visit_If(self, node):
        raise Exception(node.__dict__)

    def visit_Raise(self, node: ast.Name) -> None:
        self.tree['raises'].append(node.exc.__dict__)

    def set_slices_to_func_args(self, arg, _slice):

        self.func_data['args'][arg]['type'] = dict if isinstance(_slice, str) else list
        self.func_data['keys'][_slice][arg] = {'type': None}

    def set_type_to_func_args(self, arg, _type):
        print(arg)
        print('arg')
        if isinstance(arg, dict):
            self.func_data['keys'][arg['slice']][arg['arg']]['type'] = _type
        elif arg in self.func_data['args']:
            self.func_data['args'][arg]['type'] = _type

    def process_ast_name(self, node, variables_names, variables):
        """
            find value of 'Name' node
        :param node:
        :param variables_names:
        :param variables:
        :return:
        """
        alias = node.id
        if alias in variables_names:
            # check in variables
            variable = variables[variables_names[alias]]
            return self.get_value(variable, variables_names, variables)
        elif alias in self.func_data['args']:
            # check in function arguments
            return {'args': node.id}
        elif alias in self.tree['import']:
            # check in imports
            return {'value': node.id, 't': 'import'}
        elif alias in globals()['__builtins__']:
            # built_in name
            return {'builtin': alias}
        else:
            print(node.__dict__)
            print(node.id)
            raise Exception(node.id)

    @staticmethod
    def extract_args_in_bin_op(item, args):
        if isinstance(item, dict) and 'arg' in item:
            if 'args' in item['arg']:
                # mean this is a function arg, need to set type
                if 'slice' in item:
                    args.append({'arg': item["arg"]["args"], 'slice': item["slice"]})
                else:
                    args.append(item['arg']['args'])
        elif isinstance(item, dict) and 'args' in item:
            args.append(item['args'])
        else:
            args.append(item)
        return args

    def get_value(self, node: Any, variables_names: Dict = None, variables: Dict = None) -> Any:
        """
            extract values from different types of node
        :param node:
        :param variables_names:
        :param variables:
        :return:
        """
        node_type = node.__class__
        if not variables:
            variables = self.variables or []
        if not variables_names:
            variables_names = self.variables_names or {}
        if node_type in meta.simple:

            return node.__dict__[meta.values_for_ast_type[node_type]]
        elif node_type in meta.iterated:
            result = meta.iterated[node_type]([self.get_value(x, variables_names, variables)
                                               for x in node.__dict__[meta.values_for_ast_type[node_type]]])
            return result
        elif isinstance(node, _ast.Name):
            return self.process_ast_name(node, variables_names, variables)
        elif isinstance(node, _ast.Assign):
            return self.get_value(node.value, variables_names, variables)
        elif isinstance(node, _ast.Dict):
            return {self.get_value(key, variables_names, variables): self.get_value(
                node.values[num], variables_names, variables)
                    for num, key in enumerate(node.keys)}
        elif isinstance(node, _ast.Raise):
            return {'error': node.exc.func.id, 'comment': self.get_value(node.exc.args[0])}
        elif isinstance(node, ast.BinOp):
            bin_op_left = self.get_value(node.left, variables_names, variables)
            bin_op_right = self.get_value(node.right, variables_names, variables)
            args = []
            _simple = [int, float]
            if type(bin_op_left) in _simple and type(bin_op_right) in _simple:
                return eval(f'{bin_op_left}{meta.operators[node.op.__class__]}{bin_op_right}')
            math_type = True
            print('bin_op_left')
            print(bin_op_left)
            print(bin_op_right)
            if (isinstance(bin_op_left, dict) and 'BinOp' not in bin_op_left) \
                    and (isinstance(bin_op_right, dict) and 'BinOp' not in bin_op_right) or (
                    not (isinstance(bin_op_left, dict) or not (isinstance(bin_op_right, dict)))):
                for item in [bin_op_right, bin_op_left]:
                    args = self.extract_args_in_bin_op(item, args)
                if args and math_type:
                    for arg in args:
                        # TODO: maybe make sense to add int also
                        if isinstance(node.op, _ast.Mult) and isinstance(
                                bin_op_left, str) or isinstance(bin_op_right, str):
                            # if at least one operand is string - we can multiply only with int
                            self.set_type_to_func_args(arg, int)
                        else:
                            # mean both of them - function args
                            self.set_type_to_func_args(arg, float)
            return {'BinOp': True, 'left': bin_op_left, 'op': node.op, 'right': bin_op_right}

        elif isinstance(node, _ast.Subscript):
            arg = self.get_value(node.value,  variables_names, variables)
            slice = self.get_value(node.slice,  variables_names, variables)
            if 'args' in arg:
                self.set_slices_to_func_args(arg['args'], slice)
            return {'arg': arg, 'slice': slice}
        elif isinstance(node, _ast.Index):
            return self.get_value(node.value,  variables_names, variables)
        elif 'func' in node.__dict__:
            print(node.__dict__)
            print(node.func.__dict__)
            if 'id' in node.func.__dict__:
                print(node.func.__dict__)
                print(node.keywords)
                print(node.args[0].__dict__)
                if node.func.id == 'print':
                    return ", ".join([self.get_value(x)['text'] for x in node.args])
                if node.keywords:
                    args = [str("{}={},".format(
                        x.arg, self.get_value(x.value, variables_names, variables))) for x in node.keywords]
                    return "{}({})".format(node.func.id, "".join(args))
                else:
                    args = [self.get_value(x, variables_names, variables)
                            for x in node.args]
                    return eval("{}({})".format(node.func.id, ", ".join(args)))
            else:
                return {'func': self.get_value(node.func), 'args': node.args}
        elif isinstance(node, _ast.Compare):
            result = {'left': self.get_value(node.left, variables_names, variables),
                      'ops': self.get_value(node.ops[0], variables_names, variables),
                      'comparators': self.get_value(node.comparators[0], variables_names, variables)}
            return result
        elif type(node) in meta.operators:
            return meta.operators[type(node)]
        elif isinstance(node, _ast.Expr):
            return self.get_value(node.value)
        elif isinstance(node, _ast.Call):
            return {node.func.id: [self.get_value(arg) for arg in node.args][0]}
        elif isinstance(node, _ast.JoinedStr):
            # TODO: need to make normal process
            result = {'text': self.source[node.lineno - 1][node.col_offset:-1]}
            return result
        elif isinstance(node, _ast.FormattedValue):
            print(node.value.__dict__)
            return self.get_value(node.value)
        elif isinstance(node, _ast.UnaryOp):
            _op_map = {
                _ast.USub: '-',
                _ast.UAdd: '+',
                _ast.Invert: '~'
            }
            return eval(f'{_op_map[node.op.__class__]}{self.get_value(node.operand)}')
        elif isinstance(node, _ast.Attribute):
            value = self.get_value(node.value)
            print(value)

            return {'l_value': value, 'attr': node.attr}
        else:
            print("new type",
                  node,
                  node.__dict__)
            raise

    def get_function_args(self, body_item: _ast.Name):
        args = OrderedDict()
        for arg in body_item.args.args:
            if arg.annotation:
                if 'value' in arg.annotation.__dict__:
                    print(arg.annotation.__dict__)
                    type_arg = arg.annotation.value.id
                else:
                    print(arg.annotation.__dict__)
                    type_arg = arg.annotation.id
            else:
                type_arg = self.extract_types_from_docstring(body_item)
            args[arg.arg] = {'type': type_arg}
        return args

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        class_dict = {'name': node.name,
                      'def': defaultdict(dict),
                      'async': defaultdict(dict),
                      'args': []}

        for body_item in node.body:
            if isinstance(body_item, ast.Assign):
                var = [x.id for x in body_item.targets][0] if len(
                    body_item.targets) == 1 else [x.id for x in body_item.targets]
                if isinstance(body_item.value, _ast.List):
                    value = [self.get_value(x) for x in body_item.value.elts]
                else:
                    value = self.get_value(body_item.value)
                print('Assign', var, value)
                class_dict['args'].append((var, value))
            if not isinstance(body_item, ast.FunctionDef):
                continue

            args = self.get_function_args(body_item)
            print(args)
            defaults = []
            for item in body_item.args.defaults:
                if isinstance(item, _ast.Str):
                    defaults.append(item.s)
                elif isinstance(item, _ast.Num):
                    defaults.append(item.n)
                else:
                    print(item)
                    print(item.__dict__)
                    if 'op' in item.__dict__:
                        print(item.op.__dict__)
                        print(item.operand.__dict__)
                    defaults.append(item.value)

            if len(args) > len(defaults):
                [defaults.insert(0, 'no_default')
                 for _ in range(len(args) - len(defaults))]
            for num, arg in enumerate(args):
                args[arg]['default'] = defaults[num]

            funct_info = self.visit_FunctionDef(body_item, class_=True)
            print('funct_info')
            print(funct_info)
            if funct_info['args']:
                funct_info['doc'] = self.extract_types_from_docstring(body_item)
            for decorator in body_item.decorator_list:
                if isinstance(decorator, ast.Name) and decorator.id == 'staticmethod':
                    class_dict['def']['static'][body_item.name] = funct_info
                    break
                elif isinstance(decorator, ast.Name) and decorator.id == 'classmethod':
                    class_dict['def']['class'][body_item.name] = funct_info
                    break
            else:
                class_dict['def']['self'][body_item.name] = funct_info

        self.tree['classes'].append(class_dict)

    def visit_AsyncFunctionDef(self, node):
        self.visit_FunctionDef(node, async_f=True)

    @staticmethod
    def extract_types_from_docstring(body_item: _ast.Name) -> dict:
        """ try to get types form node
                :type class_name:
        """
        doc = ast.get_docstring(body_item)
        doc_types = {}
        if not doc or 'type' not in doc:
            doc_types['No type'] = True
        else:
            for arg in body_item.args.args:
                print('type', arg.arg, doc.split(arg.arg))
        return doc_types

    def report(self) -> None:
        pprint(self.tree)
