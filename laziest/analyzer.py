""" result of analyzers work - data from ast that needed to asserter """
import ast
import _ast
import re

from copy import deepcopy
from typing import Any, Text, Dict
from pprint import pprint
from collections import defaultdict, OrderedDict
from laziest import ast_meta as meta
from laziest.params import generate_value_in_borders
from random import randint

pytest_needed = False


class Analyzer(ast.NodeVisitor):
    """ class to parse files in dict structure to provide to generator data,
    that needed for tests generation """

    operators = {
        _ast.Eq: '==',
        _ast.Gt: '>'
    }

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

    def get_bin_op_value(self, code_line: int, variables: Dict,
                         variables_names: Dict, global_vars: Dict = None, binop_vars: Dict = None) -> Any:
        """
            method to get result value of execution BinOp

            TODO: candidate to remove from here
        :param code_line:
        :param variables:
        :param variables_names:
        :param global_vars:
        :return:
        """
        if binop_vars is None:
            binop_vars = {}
        if not global_vars:
            # create global vars dict for eval value
            global_vars = {}
        try:
            # try to eval code
            return_value = eval(code_line, global_vars)
        except NameError as name_er:
            # if no variable
            var_name = name_er.args[0].split('\'')[1]
            if name_er in self.func_data['args']:
                # if name is a function's parameter

                print(self.func_data['args'])
                print('args')
                return_value = {'BinOp': code_line, 'global_vars': binop_vars}
            elif var_name in variables_names:
                # if name in variables (assignment statements)
                print(var_name)
                print('var_name')
                variable = variables[variables_names[var_name]]
                if isinstance(variable.value, _ast.Dict):
                    # add to globals
                    binop_vars.update({var_name: {
                        self.get_value(key): self.get_value(variable.value.values[num])
                        for num, key in enumerate(variable.value.keys)}
                    })
                    global_vars.update(binop_vars)
                elif isinstance(variable.value, _ast.Name):
                    # mean that our variable linked to another
                    alias = variable.value.id
                    if alias not in global_vars and alias in variables_names:
                        variable = variables[variables_names[var_name]]
                        binop_vars.update({
                            alias: {
                                self.get_value(key, variables_names, variables):
                                    self.get_value(variable.value.values[num])
                                for num, key in enumerate(variable.value.keys)
                            }})
                        global_vars.update(binop_vars)
                    else:
                        binop_vars.update({var_name: global_vars.get(alias)})
                        global_vars.update(binop_vars)
                else:
                    binop_vars.update({var_name: self.get_value(variable.value)})
                    global_vars.update(binop_vars)
                return self.get_bin_op_value(code_line, variables, variables_names, global_vars, binop_vars)
        except Exception as e:
            global pytest_needed
            pytest_needed = True
            return_value = {'error': e.__class__.__name__, 'comment': e}
        return return_value

    def parse_bin_op(self, node, variables_names, variables, global_vars=None):
        """
            parse BinOp operation in code
        :param node:
        :param variables_names:
        :param variables:
        :param global_vars:
        :return:
        """
        if not global_vars:
            global_vars = {}
        lineno = node.lineno
        code_line = self.source[lineno - 1]
        col_offset = node.left.col_offset
        if '=' in code_line:
            left_part, code_line = code_line.split("=")[0], code_line.split("=")[1]
            col_offset -= len(left_part)
            col_offset -= 1
        if 'return' in code_line:
            code_line = code_line.replace('return ', '')
            col_offset -= 7
        if ',' in code_line:
            code_line = code_line[col_offset:].split(',')[0]
        code_line = re.sub(r'^\s+|\s+$', '', code_line)
        try:
            binop_args = {}
            variables_in_bin_op = code_line.split()
            for name in variables_in_bin_op:
                if name in variables_names:
                    binop_args.update({name: self.get_value(variables[variables_names[name]])})
                    global_vars.update(binop_args)

            return_value = self.get_bin_op_value(code_line, variables, variables_names, global_vars)
        except UnboundLocalError:
            return_value = {'BinOp': code_line, 'binop_args': binop_args}
        return return_value

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
        if 'print' in result:
            result = result['print']['text'].replace('    ', '')
        func_data['return'].append({'args': args, 'result': result})
        func_data['return'][index]['log'] = True
        for orelse in statement.orelse:
            if isinstance(orelse, _ast.If):
                func_data = self.process_if_construction(
                    orelse, func_data, variables_names, variables, previous_statements)
            elif isinstance(orelse, ast.Return):
                func_data['return'].append(self.generate_arg_based_on_previous_conditions(orelse.value, previous_statements))
        func_data['ifs'] = previous_statements
        return func_data

    def generate_arg_based_on_previous_conditions(self, return_node, previous_statements):
        return_value = self.get_value(return_node)
        print(return_value)
        print('generate_result_based_on_previous_conditions')
        if 'args' in return_value:
            _value = generate_value_in_borders(previous_statements, {return_value['args']: None})
            print(_value)
            return {'args': _value, 'result': return_value}

    def visit_FunctionDef(self, node, class_=None):
        """ main methods to """
        print(self.tree)
        func_data = {'args': self.get_function_args(node),
                     'kargs_def': node.args.kw_defaults,
                     'kargs': node.args.kwarg,
                     'return': []}

        self.func_data = func_data
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


        non_variables_nodes_bodies = [node for node in node.body if node not in variables]

        for body_item in non_variables_nodes_bodies:
            if isinstance(body_item, ast.Return):
                return_ = {'args': {}, 'result': self.get_value(body_item.value, variables_names, variables)}
                func_data['return'].append(return_)
                print('return___')
                print(return_)
            if isinstance(body_item, _ast.If):
                # if we have if statements in code
                print('IFFF')
                print(node.body[0])

                print(node.body[0])
                func_data = self.process_if_construction(body_item,
                                                              self.func_data, variables_names, variables)
                print('FUNC')
                print(func_data)
            print('BODY')
            print(body_item)

            print(body_item.__dict__)
        print(func_data['return'])
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

    def get_value(self, node: Any, variables_names: Dict = None, variables: Dict = None) -> Any:
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
            alias = node.id
            if alias in variables_names:
                variable = variables[variables_names[alias]]
                return self.get_value(variable, variables_names, variables)
            elif alias in self.func_data['args']:
                print("argument found")
                return {'args': node.id}
            else:
                print(node)
                raise Exception(node.id)
        elif isinstance(node, _ast.Assign):
            print(node.value)
            return self.get_value(node.value, variables_names, variables)
        elif isinstance(node, _ast.Dict):
            return {self.get_value(key, variables_names, variables):
                        self.get_value(node.values[num], variables_names, variables)
                    for num, key in enumerate(node.keys)}
        elif isinstance(node, _ast.Raise):
            return {'error': node.exc.func.id, 'comment': self.get_value(node.exc.args[0])}
        elif isinstance(node, ast.BinOp):
            return self.parse_bin_op(node, variables_names, variables)
        elif 'func' in node.__dict__ and node.func.id == 'dict':
            return eval("{}({})".format(node.func.id, "".join([str("{}={},".format(
                x.arg, self.get_value(x.value, variables_names, variables))) for x in node.keywords])))
        elif isinstance(node, _ast.Compare):
            result = {'left': self.get_value(node.left, variables_names, variables),
                      'ops': self.get_value(node.ops[0], variables_names, variables),
                      'comparators': self.get_value(node.comparators[0], variables_names, variables)}
            return result
        elif type(node) in self.operators:
            return self.operators[type(node)]
        elif isinstance(node, _ast.Expr):
            return self.get_value(node.value)
        elif isinstance(node, _ast.Call):
            return {node.func.id: [self.get_value(arg) for arg in node.args][0]}
        elif isinstance(node, _ast.JoinedStr):
            # TODO: need to make normal process
            print(node.__dict__)

            result = {'text': self.source[node.lineno - 1][node.col_offset:-1]}
            print(result)
            return result
        elif isinstance(node, _ast.FormattedValue):
            print(node.value.__dict__)
            return self.get_value(node.value)
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
        self.tree['async'][node.name] = {
            'args': self.get_function_args(node),
            'kargs_def': node.args.kw_defaults,
            'kargs': node.args.kwarg,
            'return': node.returns}

    def extract_type_from_node(self, body_item):
        if body_item.name == 'column_generation':
            for item in body_item.body:
                for i in ast.iter_child_nodes(item):
                    print(i, i.__dict__, 'aa')
                    if i.__dict__.get('args'):
                        if isinstance(i.args[0], _ast.Subscript):
                            print(i.args[0], i.args[0].__dict__, 'subscript')
                    for elem in ast.iter_child_nodes(i):
                        print(elem, elem.__dict__, 'child')
                        if elem.__dict__.get('args'):
                            if isinstance(elem.args[0], _ast.Subscript):
                                print(elem.args[0], elem.args[0].value.id, 'slice',
                                      self.get_value(elem.args[0].slice.value),
                                      elem.args[0].__dict__, 'subscript')
            pprint(ast.dump(body_item))

    @staticmethod
    def extract_types_from_docstring(body_item: _ast.Name) -> dict:
        """ try to get types form node """
        doc = ast.get_docstring(body_item)
        doc_types = {}
        """ :type class_name:"""
        if not doc or 'type' not in doc:
            doc_types['No type'] = True
        else:
            for arg in body_item.args.args:
                print('type', arg.arg, doc.split(arg.arg))
        return doc_types

    def report(self) -> None:
        pprint(self.tree)
