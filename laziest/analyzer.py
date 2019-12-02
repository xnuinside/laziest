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
    def __init__(self, source):
        self.tree = {"import": [],
                     "from": [],
                     "def": {},
                     "raises": [],
                     "classes": [],
                     "async": {}}
        # list of source lines
        self.source = source.split("\n")

    def visit_Import(self, node):
        for alias in node.names:
            self.tree["import"].append(alias.name)
        self.generic_visit(node)

    def visit_FromImport(self, node):
        for alias in node.names:
            self.tree["from"].append(alias.name)
        self.generic_visit(node)

    def get_bin_op_value(self, code_line, variables, variables_names, global_vars=None):
        if not global_vars:
            global_vars = {}
        try:
            return_value = eval(code_line, global_vars)
        except NameError as name_er:
            var_name = name_er.args[0].split('\'')[1]
            print(var_name)
            if var_name in variables_names:
                variable = variables[variables_names[var_name]]
                print(variable.__dict__)
                print(variables_names)
                print(variables)
                # create global vars dict for eval value
                if isinstance(variable.value, _ast.Dict):
                    global_vars.update({var_name: {self.get_value(key):
                                                       self.get_value(variable.value.values[num])
                                                   for num, key in enumerate(variable.value.keys)}})
                elif isinstance(variable.value, _ast.Name):
                    # mean that our variable linked to another
                    alias = variable.value.id
                    print(alias)
                    print('we are here')
                    if alias not in global_vars and alias in variables_names:
                        variable = variables[variables_names[var_name]]
                        global_vars.update({alias: {key.s: variable.value.values[num].n for num, key in enumerate(
                            variable.value.keys)}})
                    elif alias not in global_vars:
                        raise
                    global_vars.update({var_name: global_vars.get(alias)})
                return self.get_bin_op_value(code_line, variables, variables_names, global_vars)
        except Exception as e:
            global pytest_needed
            pytest_needed = True
            return_value = {'error': (e.__class__, e, )}
        return return_value

    def parse_bin_op(self, node, variables_names, variables):
        lineno = node.lineno
        code_line = self.source[lineno - 1]

        if '=' in code_line:
            code_line = code_line.split("=")[1]
        if 'return' in code_line:
            code_line = code_line.replace('return ', '')
        code_line = re.sub(r'^\s+|\s+$', '', code_line)
        return_value = self.get_bin_op_value(code_line, variables, variables_names)
        return return_value

    def visit_FunctionDef(self, node):
        print(node.name, node.__dict__)
        print(node.returns)
        print(node.body)
        func = {'args': self.get_function_args(node),
                'kargs_def': node.args.kw_defaults,
                'kargs': node.args.kwarg,
                'return': None}
        print(node.body)
        # local variables, assign statements in function body
        variables = [node for node in node.body if isinstance(node, ast.Assign)]
        variables_names = {}
        print(variables)
        if variables:
            for index, var in enumerate(variables):
                var_names =  {name_node.id: index for name_node in var.targets}
                variables_names.update(var_names)
        print(variables_names)
        non_variables_body = [node for node in node.body if node not in variables]
        for body_item in non_variables_body:
            if isinstance(body_item, ast.Return):
                print("we are here")
                func['return'] = self.get_value(body_item.value, variables_names, variables)

        self.tree['def'][node.name] = func

    def visit_Raise(self, node: ast.Name) -> None:
        self.tree['raises'].append(node.exc.__dict__)

    def get_value(self, node: Any, variables_names=None, variables=None):
        node_type = node.__class__
        print(node_type)
        print(node.__dict__)
        if node_type in meta.simple:
            print(node_type)
            print('we are here1')
            print(node.__dict__[meta.values_for_ast_type[node_type]])
            return node.__dict__[meta.values_for_ast_type[node_type]]
        elif node_type in meta.iterated:
            return meta.iterated[node_type]([self.get_value(x, variables_names, variables)
                                             for x in node.__dict__[meta.values_for_ast_type[node_type]]])
        elif isinstance(node, _ast.Name):
            alias = node.id
            print(alias)
            print('we are here')
            if alias in variables_names:
                variable = variables[variables_names[alias]]
                return self.get_value(variable, variables_names, variables)
            return node.id
        elif isinstance(node, _ast.Assign):
            return self.get_value(node.value, variables_names, variables)
        elif isinstance(node, _ast.Dict):
            return {self.get_value(key, variables_names, variables):
                        self.get_value(node.values[num], variables_names, variables)
                    for num, key in enumerate(node.keys)}
        elif isinstance(node, ast.BinOp):
            return self.parse_bin_op(node, variables_names, variables)
        elif 'func' in node.__dict__ and node.func.id == 'dict':
            return eval("{}({})".format(node.func.id, "".join([str("{}={},".format(
                x.arg, self.get_value(x.value, variables_names, variables))) for x in node.keywords])))
        elif 'func' in node.__dict__:
            print(node.func.__dict__)
            try:
                result = eval("{}({})".format(node.func.id,
                                              [str(self.get_value(x)) for x in node.args]))
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
