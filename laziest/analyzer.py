import ast
import _ast
import re
from typing import Any, Union
from pprint import pprint
from collections import defaultdict, OrderedDict
from laziest import ast_meta as meta

pytest_needed = False


class NotDefault(object):
    """special class to indicate args with no default values"""
    def __repr__(self):
        return 'no_default'


no_default = NotDefault()


class Analyzer(ast.NodeVisitor):
    """ class to parse files in dict structure to provide to generator data,
    that needed for tests generation """

    current_state = None

    def __init__(self, source):
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
        Analyzer.current_state = self

    def visit_Import(self, node):
        for alias in node.names:
            self.tree["import"].append(alias.name)
        self.generic_visit(node)

    def visit_FromImport(self, node):
        for alias in node.names:
            self.tree["from"].append(alias.name)
        self.generic_visit(node)

    def get_bin_op_value(self, code_line, variables, variables_names, global_vars=None):
        print('parse_bin_op')
        print(variables_names, variables)
        if not global_vars:
            global_vars = {}
        try:
            print(code_line)
            print(global_vars)
            return_value = eval(code_line, global_vars)
        except NameError as name_er:
            print(name_er)
            var_name = name_er.args[0].split('\'')[1]
            print('var_name')
            print(var_name)
            if name_er in self.func_data['args']:
                return_value = {'BinOp': code_line, 'global_vars': global_vars}
            elif var_name in variables_names:
                print('variables_names')
                variable = variables[variables_names[var_name]]
                print(variable.__dict__)
                print(variables_names)
                print(variables)
                # create global vars dict for eval value
                print('variable.value')
                print(variable.value)
                if isinstance(variable.value, _ast.Dict):

                    global_vars.update({var_name: {self.get_value(key):
                                                       self.get_value(variable.value.values[num])
                                                   for num, key in enumerate(variable.value.keys)}})
                elif isinstance(variable.value, _ast.Name):
                    # mean that our variable linked to another
                    alias = variable.value.id
                    print(alias)
                    print('we are here3')
                    if alias not in global_vars and alias in variables_names:
                        variable = variables[variables_names[var_name]]
                        global_vars.update(
                            {alias: {self.get_value(key, variables_names, variables):
                                         self.get_value(variable.value.values[num])
                                     for num, key in enumerate(variable.value.keys)}})
                    else:
                        global_vars.update({var_name: global_vars.get(alias)})
                else:
                    global_vars.update({var_name: self.get_value(variable.value)})
                return self.get_bin_op_value(code_line, variables, variables_names, global_vars)
        except Exception as e:
            global pytest_needed
            pytest_needed = True
            return_value = {'error': (e.__class__, e, )}
        print(variables_names, variables)
        return return_value

    def parse_bin_op(self, node, variables_names, variables, global_vars=None):
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
        print('col_offset', col_offset)
        if ',' in code_line:
            print(code_line)
            print(code_line[col_offset:])
            code_line = code_line[col_offset:].split(',')[0]
        code_line = re.sub(r'^\s+|\s+$', '', code_line)
        print('code_line123')
        print(code_line)
        try:
            variables_in_bin_op = code_line.split()
            for name in variables_in_bin_op:
                if name in variables_names:
                    print('binop1', name)
                    print(variables[variables_names[name]])
                    global_vars.update({name: self.get_value(variables[variables_names[name]])})
            return_value = self.get_bin_op_value(code_line, variables, variables_names, global_vars)
        except UnboundLocalError:
            return_value = {'BinOp': code_line, 'global_vars': global_vars}
        return return_value

    def visit_FunctionDef(self, node, class_=None):
        print(node.name, node.__dict__)
        print(node.returns)
        print(node.body)
        func_data = {'args': self.get_function_args(node),
                     'kargs_def': node.args.kw_defaults,
                     'kargs': node.args.kwarg,
                     'return': None}
        if not class_:
            self.func_data = func_data
        # local variables, assign statements in function body
        variables = [node for node in node.body if isinstance(node, ast.Assign)]
        variables_names = {}
        print('variables_s')
        if isinstance(node.body[0], _ast.If):
            print('Iff')
            print(node.body[0].__dict__)
            print(node.body[0].test.__dict__)
            statement = node.body[0].test
            # we get variables from statement
            print(statement)
            value = self.get_value(statement.left, variables_names, variables)
            print('if value from statement')
            print(value)
            # we work with args from statements
            if isinstance(value, dict) and 'arg' in value:
                if 'if' not in func_data['args'][value['arg']]:
                    func_data['args'][value['arg']]['if'] = {}
                if 'values' not in func_data['args'][value['arg']]['if']:
                    func_data['args'][value['arg']]['if']['values'] = [self.get_value(
                        statement.comparators[0], variables_names, variables)]
                    print('hi')
                else:
                    func_data['args'][value['arg']]['if']['values'].append(value)
                # we need to get return for this value
                print(func_data['args'][value['arg']])
                body = node.body[0].body[0]
                if_return = self.get_value(body)
                if 'return' not in func_data['args'][value['arg']]['if']:
                    func_data['args'][value['arg']]['if']['return'] = [if_return]
                else:
                    func_data['args'][value['arg']]['if']['return'].append(if_return)
                print('if_return')
                print(if_return)
            print('body')
            print(node.body[0].body[0].__dict__)
            print(node.body[0].body[0].exc.__dict__)
            print(node.body[0].body[0].exc.func.id)

        print(variables)
        if variables:
            for index, var in enumerate(variables):
                var_names = {name_node.id: index for name_node in var.targets}
                variables_names.update(var_names)
        print(variables_names)
        from copy import deepcopy
        self.variables = variables
        self.variables_names = deepcopy(variables_names)
        non_variables_body = [node for node in node.body if node not in variables]
        for body_item in non_variables_body:
            if isinstance(body_item, ast.Return):
                print("we are here2")
                func_data['return'] = self.get_value(body_item.value, variables_names, variables)
                print(func_data['return'])
        if not class_:
            self.tree['def'][node.name] = func_data
        return func_data

    def visit_If(self, node):
        raise Exception(node.__dict__)

    def visit_Raise(self, node: ast.Name) -> None:
        self.tree['raises'].append(node.exc.__dict__)

    def get_value(self, node: Any, variables_names=None, variables=None):
        node_type = node.__class__
        if not variables:
            variables = self.variables or []
        if not variables_names:
            variables_names = self.variables_names or {}
        print('valueee')
        print(node_type)
        print(node.__dict__)
        print(variables_names)

        if node_type in meta.simple:
            print(node_type)
            print('we are here1')
            print(node.__dict__[meta.values_for_ast_type[node_type]])
            return node.__dict__[meta.values_for_ast_type[node_type]]
        elif node_type in meta.iterated:
            print('iterating')
            result = meta.iterated[node_type]([self.get_value(x, variables_names, variables)
                                               for x in node.__dict__[meta.values_for_ast_type[node_type]]])
            print(result)
            return result
        elif isinstance(node, _ast.Name):
            alias = node.id
            print(node.__dict__)
            print(node.ctx)
            print('we are here00')
            if alias in variables_names:
                variable = variables[variables_names[alias]]
                print(variable.__dict__)
                print('we are here200')
                return self.get_value(variable, variables_names, variables)
            elif alias in self.func_data['args']:
                    print("argument found")
                    return {'arg': node.id}
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
            print(node.exc)
            print(node.exc.__dict__)
            print(node.exc.func)
            print(node.exc.args[0].__dict__)
            print(node.exc.func.__dict__)
            print(node.exc.func.ctx)

            print(node.exc.func.ctx.__dict__)
            return {'error': node.exc.func.id}
        elif isinstance(node, ast.BinOp):
            return self.parse_bin_op(node, variables_names, variables)
        elif 'func' in node.__dict__ and node.func.id == 'dict':
            return eval("{}({})".format(node.func.id, "".join([str("{}={},".format(
                x.arg, self.get_value(x.value, variables_names, variables))) for x in node.keywords])))
        elif 'func' in node.__dict__:
            print(node.func.__dict__)
            try:
                result = eval("{}({})".format(node.func.id,
                                              [str(self.get_value(x, variables_names, variables)) for x in node.args]))
            except NameError as e:
                print('NameError', e.args)
                result = None
            return result

        else:
            print("new type", node, node.__dict__)
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
                [defaults.insert(0, no_default)
                 for _ in range(len(args) - len(defaults))]
            for num, arg in enumerate(args):
                args[arg]['default'] = defaults[num]

            funct_info = {
                'args': args,
                'return': body_item.returns,
            }
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
