import ast
import _ast
from typing import Any, Union
from pprint import pprint
from collections import defaultdict, OrderedDict


class NotDefault(object):
    """special class to indicate args with no default values"""
    def __repr__(self):
        return 'no_default'


no_default = NotDefault()


class Analyzer(ast.NodeVisitor):
    """ class to parse files in dict structure to provide to generator data,
    that needed for tests generation """
    def __init__(self):
        self.tree = {"import": [],
                     "from": [],
                     "def": {},
                     "raises": [],
                     "classes": [],
                     "async": {}}

    def visit_Import(self, node):
        for alias in node.names:
            self.tree["import"].append(alias.name)
        self.generic_visit(node)

    def visit_FromImport(self, node):
        for alias in node.names:
            self.tree["from"].append(alias.name)
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        self.tree['def'][node.name] = {
                                  'args': self.get_function_args(node),
                                  'kargs_def': node.args.kw_defaults,
                                  'kargs': node.args.kwarg,
                                  'return': node.returns}

    def visit_Raise(self, node: ast.Name) -> None:
        self.tree['raises'].append(node.exc.__dict__)

    def get_value(self, var: Any) -> None:
        if isinstance(var, _ast.Str):
            return var.s
        elif isinstance(var, _ast.Num):
            return var.n
        elif 'func' in var.__dict__ and var.func.id == 'dict':
            return eval("{}({})".format(var.func.id, "".join([str("{}={},".format(
                x.arg, self.get_value(x.value))) for x in var.keywords])))
        elif 'func' in var.__dict__:
            print(var.func.__dict__)
            try:
                result = eval("{}({})".format(var.func.id,
                                            [str(self.get_value(x)) for x in var.args]))
            except NameError as e:
                print('NameError', e.args)
                result = None
            return result
        else:
            print("new type", var.__dict__)
            return None

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
