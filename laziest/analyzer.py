""" result of analyzers work - data from ast that needed to asserter """
import ast
import _ast
from copy import deepcopy
from typing import Any, Text, Dict, Union, List, Tuple
from pprint import pprint
from collections import defaultdict, OrderedDict
from laziest import ast_meta as meta

pytest_needed = False
jedi_param_type_line = 'param {param_name}: '


class StrategyAny:
    pass


class Analyzer(ast.NodeVisitor):
    """ class to parse files in dict structure to provide to generator data,
    that needed for tests generation """

    def __init__(self, source: Text, debug: bool):
        """
            source - code massive
        :param debug:
        :param source:
        """
        self.debug = debug
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

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            self.tree["import"].append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: _ast.ImportFrom):
        for alias in node.names:
            self.tree["from"].append(alias.name)
        self.generic_visit(node)

    @staticmethod
    def get_operand_value(value: Any):
        """ arg can be single like int, str and etc or it can be slice like dict, list, tuple and etc.
            sample with slice {'arg': {'args': 'arg1'}, 'slice': 3}
        """
        if isinstance(value, dict):
            if 'slice' in value:
                value = f'{value["arg"]["args"]}[\'{value["slice"]}\']' if isinstance(
                    value['slice'], str) else f'{value["arg"]["args"]}[{value["slice"]}]'
            elif 'args' in value:
                value = value['args']
        return value

    def process_if_construction(self, statement: _ast.If, func_data: Dict,
                                variables_names: Dict, variables: List,
                                previous_statements: List = None):
        if previous_statements is None:
            previous_statements = []
        # we get variables from statement
        values = self.get_value(statement.test, variables_names, variables)
        # we work with args from statements
        args = {}
        _conditions_op = None
        variables_names = deepcopy(variables_names)
        variables = deepcopy(variables)
        if_variables, if_variables_names = self.extract_variables_in_scope(statement, variables, variables_names)

        if len(statement.body) > 1:
            for body_node in statement.body[:-1]:
                self.process_body_node(body_node, variables_names, variables, in_if=True)
        result = self.get_value(statement.body[-1], if_variables_names, if_variables)
        if 'print' in result:
            result = result['print']['text'].strip()
        return_pack = {'args': args, 'result': result}
        if '\'' in result:
            # TODO: this is a hack, need to normalize it
            return_pack['log'] = True
        if 'comparators' not in values:
            # or/and between conditions
            _conditions_op = self.get_value(values['op'])
            _values = []
            for value in values['values']:
                if 'left' not in value:
                    _type = self.func_data['args'][value['args']]['type']
                    value = {'left': value, 'comparators': meta.empty_types[_type], 'ops': '!='}
                _values.append(value)
            values = _values
        if not isinstance(values, list):
            values = [values]
        if _conditions_op == 'or':
            for value in values:
                previous_statements.append([value])
                func_data['return'].append(return_pack)
        else:
            previous_statements.append(values)
            func_data['return'].append(return_pack)

        for orelse in statement.orelse:
            if isinstance(orelse, _ast.If):
                func_data = self.process_if_construction(
                    orelse, func_data, variables_names, variables, previous_statements)
            elif isinstance(orelse, ast.Return):
                func_data['return'].append(self.get_value(orelse))
        func_data['ifs'] = previous_statements
        return func_data

    def separate_assing_nodes(self, node: _ast.Assign, variables_names, variables):
        if isinstance(node.targets[0], _ast.Tuple):
            tuple_key = meta.values_for_ast_type[type(node.targets[0])]
            for num, target_node in enumerate(getattr(node.targets[0], tuple_key)):
                if isinstance(node.value, _ast.Tuple):
                    inner_value = getattr(node.value, tuple_key)[num]
                else:
                    node_value = self.get_value(node.value, variables_names, variables)
                    if isinstance(node_value, dict):
                        inner_value = _ast.Subscript(value=node.value, slice=_ast.Index(value=_ast.Num(n=num)))
                    else:
                        inner_value = node_value
                var = _ast.Assign(targets=[target_node], value=inner_value)
                yield var
        elif isinstance(node.value, _ast.List):
            for target in node.targets:
                for elem in node.value.elts:
                    # for items
                    var = _ast.Assign(targets=[target], value=elem)
                    yield var
        elif isinstance(node.value, _ast.Call):
            value = self.get_value(node.value, variables_names, variables)
            for target in node.targets:
                # for items in call result
                var = _ast.Assign(targets=[target], value=value)
                yield var

    def extract_variables_in_scope(self,
                                   node: Union[ast.FunctionDef, _ast.If, _ast.For],
                                   variables: List = None,
                                   variables_names: Dict = None,
                                   main_run: bool = False):

        """
            method to extract variables and variables names, that used in scope
        :param node:
        :param variables:
        :param variables_names:
        :param main_run:
        :return:
        """
        # local variables, assign statements in function body
        # variables 'id' -> Name node, 'value' -> Node
        if not variables:
            variables = []
            variables_names = {}

        for node in node.body:
            if getattr(node, 'body', None) and not isinstance(node, _ast.For):
                _variables, _ = self.extract_variables_in_scope(node)
                variables += _variables

            if isinstance(node, _ast.Assign):
                if getattr(node.targets[0], 'id', None) and node.targets[0].id not in self.func_data['args']:
                    # for single assignments var2 = 1
                    variables.append(node)
                elif isinstance(node.targets[0], _ast.Tuple):
                    # in one Assign node can be several targets and values, like var1, var2 = 1, 2 (multi assign)
                    for var in self.separate_assing_nodes(node, variables_names, variables):
                        if var.targets[0].id not in self.func_data['args']:
                            variables.append(var)

            elif isinstance(node, _ast.If):
                _variables, _ = self.extract_variables_in_scope(node, variables, variables_names)
                variables += _variables
        variables_names = {}
        if variables:
            # define code variables in dict
            for index, var in enumerate(variables):
                var_names = {name_node.id: index for name_node in var.targets}
                variables_names.update(var_names)
        if main_run:
            self.variables = variables
            self.variables_names = deepcopy(variables_names)
            self.func_data['variables'] = self.variables
        return variables, variables_names

    def check_arg_in_assing_node(self, node: _ast.Assign) -> Tuple[bool, bool]:
        # need find if arg used in some variable (in right sight) or maybe modified with same name - to find steps
        if getattr(node, 'target', None):
            if node.target.id in self.func_data['args'] or node.target.id in self.func_data[
                    'steps_dependencies']:
                return True, False
        elif getattr(node, 'targets', None):
            if getattr(node.targets[0], 'id', None):
                if node.targets[0].id in self.func_data['args']:
                    # operations like arg_1 *= 10
                    # if at the left function arg name
                    return True, False
                elif node.targets[0].id in self.func_data[
                        'steps_dependencies']:
                    return True, False
        if getattr(node, 'value', None):
            if (getattr(node.value, 'id', None) and node.value.id in self.func_data['args']) or (
                    getattr(node.value, 'id', None) and node.value.id in self.func_data['steps_dependencies']):
                return True, True
            elif isinstance(node.value, _ast.Tuple):
                for inner_node in node.value.elts:
                    if getattr(inner_node, 'id', None) and inner_node.id in self.func_data['args'] or \
                            getattr(inner_node, 'id', None) and inner_node.id in self.func_data['steps_dependencies']:
                        return True, True
            elif isinstance(node.value, _ast.Call):
                func = node.value.func
                if not isinstance(func, _ast.Name):
                    if getattr(func.value, 'id', None) and func.value.id \
                            in self.func_data['args'] or func.value.id in self.func_data['steps_dependencies']:
                        return True, True
        return False, False

    def process_for_node(self, node, variables_names, variables):
        for var in self.separate_assing_nodes(_ast.Assign(targets=[node.target], value=node.iter),
                                              variables_names, variables):
            variables.append(var)
            _index = len(variables) - 1
            variables_names[var.targets[0].id] = _index
            for inner_node in node.body:
                self.process_body_node(inner_node, variables_names, variables)
        return variables

    def process_body_node(self, node: Any, variables_names: Dict, variables: List, in_if: bool = False):

        step, arg_in_value = self.check_arg_in_assing_node(node)

        if isinstance(node, ast.Return):
            if getattr(node.value, 'id', None) and node.value.id in self.func_data['steps_dependencies']:
                return_ = {'result': {'var': node.value.id}}
            else:
                return_ = {'result': self.get_value(node.value, variables_names, variables)}
            self.func_data['return'].append(return_)
        elif isinstance(node, _ast.If):
            self.func_data = self.process_if_construction(
                node, self.func_data, variables_names, variables)
        elif getattr(node, 'targets', None) and isinstance(node.targets[0], _ast.Tuple):
            for inner_node in self.separate_assing_nodes(node, variables_names, variables):
                step, arg_in_value = self.check_arg_in_assing_node(inner_node)
                if step:
                    # if at the left function arg name
                    self.add_step_for_arg(inner_node, variables_names, variables, arg_in_value)
        elif step:
            # operations like arg_1 *= 10
            self.add_step_for_arg(node, variables_names, variables, arg_in_value)
        elif isinstance(node, _ast.Pass):
            return
        elif isinstance(node, _ast.For):
            self.process_for_node(node, variables_names, variables)
        else:
            print(node)
            print(node.__dict__)
            if in_if:
                return
            raise

    def function_data_base(self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef], async_f: bool) -> Dict:
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
                          'variables': [],
                          'steps': {},
                          'steps_dependencies': {},
                          'for': {}}
        return self.func_data

    def visit_FunctionDef(self, node: ast.FunctionDef, async_f: bool = False, class_: Dict = None):
        """ main methods to """
        try:
            func_data = self.function_data_base(node, async_f)
            variables, variables_names = self.extract_variables_in_scope(node, main_run=True)
            non_variables_nodes_bodies = [node for node in node.body if node not in variables]
            for body_item in non_variables_nodes_bodies:
                self.process_body_node(body_item, variables_names, variables)
            for result in func_data['return']:
                result = result['result']
                if isinstance(result, dict) and 'func' in result:
                    arg = result['args']
                    if isinstance(arg, dict) and 'args' in arg:
                        arg = arg['args']
                    if not isinstance(arg, dict) and arg in self.func_data['args']:
                        # mean in function we use upper function argument
                        self.identify_type_by_attr(arg, result['func'], variables, variables_names)
            func_data = self.form_strategies(func_data)

            if not func_data['return']:
                # if function does not return anything
                func_data['return'] = [{'args': (), 'result': None}]
            for arg, value in func_data['args'].items():
                if value.get('type') is None:
                    # set default type
                    func_data['args'][arg]['type'] = int
            if not class_:
                self.tree['def'][node.name] = deepcopy(func_data)
        except Exception as e:
            if self.debug:
                func_data = {'error': e.__class__.__name__, 'comment': e}
            else:
                raise e
        return func_data

    def visit_If(self, node: ast.If):
        raise Exception(node.__dict__)

    def visit_Raise(self, node: ast.Name) -> None:
        self.tree['raises'].append(node.exc.__dict__)

    def add_step_for_arg(self, node, variables_names: Dict, variables: List, in_value: bool = False):
        arg_name = None
        if getattr(node, 'target', None):
            var_name = node.target.id
        elif getattr(node, 'targets', None):
            var_name = node.targets[0].id
        if in_value:
            if getattr(node.value, 'id', None):
                if node.value.id in self.func_data['args']:
                    arg_name = node.value.id
            elif isinstance(node.value, _ast.Tuple):
                for inner_node in node.value.elts:
                    if inner_node.id in self.func_data['args']:
                        arg_name = inner_node.id
            elif isinstance(node.value, _ast.Call):
                func = node.value.func
                if getattr(func.value, 'id', None):
                    if func.value.id in self.func_data['args']:
                        arg_name = func.value.id
        if not arg_name:
            if var_name in self.func_data['steps_dependencies']:
                arg_name = self.func_data['steps_dependencies'][var_name]
        if var_name not in self.func_data['args']:
            # TODO: need to add work around when as var used different function arg
            self.func_data['steps_dependencies'][var_name] = arg_name
        else:
            arg_name = var_name
        if not arg_name:
            raise
        if arg_name not in self.func_data['steps']:
            self.func_data['steps'][arg_name] = []
        step = self.get_value(node, variables_names, variables)
        if isinstance(step, dict) and 'func' in step:
            self.set_type_by_attrib(arg_name, step['func']['attr'])
        self.func_data['steps'][arg_name].append({'var_name': var_name, 'step': step})

    def set_slices_to_func_args(self, arg: Text, _slice: Union[Text, int]):

        self.func_data['args'][arg]['type'] = dict if isinstance(_slice, str) else list
        self.func_data['keys'][_slice][arg] = {'type': None}

    def set_type_to_func_args(self, arg: Union[Text, Dict], _type: Any):
        optional = 'Optional['
        if isinstance(_type, str) and optional in _type:
            _type = _type.split(optional)[1].split(']')[0]
        if isinstance(arg, dict) and arg.get('arg'):
            arg_name = arg.get('arg')
            if isinstance(arg_name, dict) and 'args' in arg_name:
                arg_name = arg_name['args']
            if 'slice' in arg:
                self.func_data['keys'][arg['slice']][arg_name]['type'] = _type
        elif isinstance(arg, dict) and arg.get('args'):
            arg_name = arg['args']
            if 'slice' in arg:
                self.func_data['keys'][arg['slice']][arg_name]['type'] = _type
        elif arg in self.func_data['args']:
            self.func_data['args'][arg]['type'] = _type
        return _type

    def process_ast_name(self, node: _ast.Name, variables_names: Dict, variables: List):
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
            print(node)
            raise Exception(node.id)

    @staticmethod
    def extract_args_in_bin_op(item: Union[Dict, Any], args: List):
        if isinstance(item, dict) and 'arg' in item:
            if 'args' in item['arg']:
                # mean this is a function arg, need to set type
                if 'slice' in item:
                    args.append({'arg': item["arg"]["args"], 'slice': item["slice"]})
                else:
                    args.append(item['arg']['args'])
        elif isinstance(item, dict) and 'args' in item:
            if item['args']:
                args.append(item['args'])
        else:
            if not isinstance(item, dict):
                args.append(item)
            elif item:
                # if for some reason come dict with args
                raise
        return args

    def get_value(self, node: Any, variables_names: Dict = None, variables: List = None) -> Any:
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
            if isinstance(node.targets[0], _ast.Tuple):
                return self.separate_assing_nodes(node, variables_names, variables)
            return self.get_value(node.value, variables_names, variables)
        elif isinstance(node, _ast.Dict):
            return {self.get_value(key, variables_names, variables): self.get_value(
                node.values[num], variables_names, variables)
                    for num, key in enumerate(node.keys)}
        elif isinstance(node, _ast.Raise):
            return {'error': node.exc.func.id, 'comment': self.get_value(node.exc.args[0])}
        elif isinstance(node, ast.BinOp):
            # TODO: need to refactor this
            bin_op_left = self.get_value(node.left, variables_names, variables)
            bin_op_right = self.get_value(node.right, variables_names, variables)
            args = []
            sides = [bin_op_left, bin_op_right]
            _simple = [int, float]
            if type(bin_op_left) in _simple and type(bin_op_right) in _simple:
                # count result of bin op
                return eval(f'{bin_op_left}{meta.operators[node.op.__class__]}{bin_op_right}')
            math_type = True
            if (isinstance(node.left, _ast.Str) or isinstance(node.right, _ast.Str))\
                    and isinstance(node.op, _ast.Add):
                # concatination
                math_type = False
            if (isinstance(bin_op_left, dict) and 'BinOp' not in bin_op_left) \
                    and (isinstance(bin_op_right, dict) and 'BinOp' not in bin_op_right) or (
                    not (isinstance(bin_op_left, dict) or not (isinstance(bin_op_right, dict)))):
                for item in [bin_op_right, bin_op_left]:
                    args = self.extract_args_in_bin_op(item, args)
                if args:
                    for arg in args:
                        if math_type:
                            _type = None
                            # TODO: need to refactor all this logic about assigne types by operations
                            if (isinstance(arg, dict) and 'slice' not in arg) or not isinstance(arg, dict):
                                if isinstance(bin_op_left, dict) and 'slice' in bin_op_left:
                                    _type = self.func_data['keys'][bin_op_left['slice']][
                                        bin_op_left['arg']['args']]['type']
                                elif isinstance(bin_op_right, dict) and 'slice' in bin_op_right:
                                    _type = self.func_data['keys'][bin_op_right['slice']][
                                        bin_op_right['arg']['args']]['type']
                                if _type:
                                    self.set_type_to_func_args(arg, _type)
                            if not _type:
                                if (isinstance(node.op, _ast.Mult) or isinstance(node.op, _ast.Add)) and \
                                        isinstance(bin_op_left, str) or isinstance(bin_op_right, str):
                                    # if at least one operand is string - we can multiply only with int
                                    self.set_type_to_func_args(arg, int)
                                else:
                                    # mean both of them - function args
                                    if isinstance(arg, dict):
                                        self.set_type_to_func_args(arg, float)
                                    elif not self.func_data['args'].get(arg, {}).get('type'):
                                        self.set_type_to_func_args(arg, float)

                        else:
                            self.set_type_to_func_args(arg, str)

            for side in sides:
                # TODO: need refactor all this logic with setting type by binop
                opposite_side = [x for x in sides if x != side]
                if isinstance(side, dict) and ('args' in side or 'arg' in side) \
                        and opposite_side and 'func' not in side:
                    if side.get('args', None):
                        _side_args = side.get('args', None)
                    elif side.get('arg'):
                        # with slice
                        _side_args = side
                    opposite_side = opposite_side[0]
                    if isinstance(_side_args, list):
                        # TODO: maybe for arg in args?
                        _side_args = _side_args[0]
                    if isinstance(_side_args, dict) and 'slice' in _side_args:
                        if 'args' not in _side_args['arg']:
                            # mean we have simple dict
                            continue
                        _arg_name = _side_args['arg']['args']
                    elif isinstance(_side_args, dict) and 'func' in _side_args:
                        # need check by func
                        continue
                    else:
                        _arg_name = _side_args
                    if 'slice' not in _side_args:
                        _type_check = bool(self.func_data['args'][_arg_name]['type'])
                    else:
                        _type_check = bool(self.func_data['keys'][_side_args['slice']][_arg_name]['type'])
                    if isinstance(side, dict) and _side_args and not _type_check:
                        if isinstance(opposite_side, dict):
                            if 'args' in opposite_side:
                                self.set_type_to_func_args(_side_args,
                                                           self.func_data['args'][opposite_side['args']]['type'])
                            elif 'BinOp' in opposite_side:
                                if 'args' in opposite_side['left']:
                                    self.set_type_to_func_args(
                                        _side_args, self.func_data['args'][opposite_side['left']['args']]['type'])
                            _type = True
            return {'BinOp': True, 'left': bin_op_left, 'op': node.op, 'right': bin_op_right}

        elif isinstance(node, _ast.Subscript):
            arg = self.get_value(node.value,  variables_names, variables)
            _slice = self.get_value(node.slice,  variables_names, variables)
            if 'args' in arg and 'func' not in arg:
                self.set_slices_to_func_args(arg['args'], _slice)
            return {'arg': arg, 'slice': _slice}
        elif isinstance(node, _ast.Index):
            return self.get_value(node.value,  variables_names, variables)
        elif isinstance(node, dict):
            return node
        elif 'func' in node.__dict__:
            if 'id' in node.func.__dict__:
                if node.func.id == 'print':
                    return ", ".join([self.get_value(x)['text'] for x in node.args])
                if node.keywords:
                    args = [str("{}={},".format(
                        x.arg, self.get_value(x.value, variables_names, variables))) for x in node.keywords]
                    return {'func': node.func.id, 'args': "".join(args)}
                else:
                    args = [self.get_value(x, variables_names, variables)
                            for x in node.args]
                    if 'args' in args[0]:
                        return {'func': node.func.id, 'args': args}
                    else:
                        return eval("{}({})".format(node.func.id, ", ".join(args)))
            else:
                if node.args:
                    arg = self.get_value(node.args[0], variables_names, variables)
                else:
                    arg = {}
                func = self.get_value(node.func, variables_names, variables)
                result = {'func': func, 'args': arg}
                return result
        elif isinstance(node, _ast.Compare):
            result = {'left': self.get_value(node.left, variables_names, variables),
                      'ops': self.get_value(node.ops[0], variables_names, variables),
                      'comparators': self.get_value(node.comparators[0], variables_names, variables)}
            if 'args' in result['left']:
                # TODO: need to change this, because one arg can be several diff types for diff result
                self.set_type_to_func_args(result['left']['args'],
                                           type(result['comparators']))
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
            return self.get_value(node.value)
        elif isinstance(node, _ast.UnaryOp):
            _op_map = {
                _ast.USub: '-',
                _ast.UAdd: '+',
                _ast.Invert: '~'
            }
            return eval(f'{_op_map[node.op.__class__]}{self.get_value(node.operand)}')
        elif isinstance(node, _ast.Attribute):
            if getattr(node.value, 'id', None) and getattr(node.value, 'id', None) in self.func_data['args']:
                # TODO: need to add with slice
                self.set_type_by_attrib(node.value.id, node.attr)
            value = self.get_value(node.value, variables_names, variables)
            attr = self.get_attr_call_line(node)
            return {'l_value': value, 'attr': attr}
        elif isinstance(node, _ast.Return):
            return {'result': self.get_value(node.value, variables_names, variables)}
        elif isinstance(node, _ast.AugAssign):
            # arg_1 *= 10 operations
            arg = self.get_value(node.target, variables_names, variables)
            # TODO: need to modify type set, can be str also
            if not isinstance(arg['args'], dict):
                if not self.func_data['args'][arg['args']].get('type') or (
                    isinstance(self.func_data['args'][arg['args']]['type'], dict)
                        and self.func_data['args'][arg['args']]['type'] is None):
                    self.set_type_to_func_args(arg['args'], int)
            if 'args' in arg:
                return {'arg': arg,
                        'op': f'{meta.operators[node.op.__class__]}',
                        'l_value': self.get_value(node.value, variables_names, variables)}
            else:
                raise
        elif isinstance(node, _ast.NameConstant):
            # True - False
            return node.value
        elif isinstance(node, _ast.In):
            # True - False
            return 'in'
        elif isinstance(node, _ast.NotIn):
            return 'not in'
        elif isinstance(node, _ast.BoolOp):
            return {'op': node.op, 'values': [self.get_value(
                value, variables_names, variables) for value in node.values]}
        else:
            print("new type",
                  node,
                  node.__dict__)
            raise

    @staticmethod
    def reverse_condition(statement: Dict) -> Dict:
        not_statement = deepcopy(statement)
        # change to opposite in pair != to == > to <= and etc
        not_statement['ops'] = meta.ops_pairs[not_statement['ops']]
        # mean that this is reversed from previous strategy,
        # we don't need to reverse it in next strategies
        not_statement['previous'] = True
        return not_statement

    def reverse_condition_group(self, statement_group: Union[Dict, List]) -> Dict:
        if isinstance(statement_group, list):
            not_statement_group = []
            for statement in statement_group:
                not_statement_group.append(self.reverse_condition(statement))
            return not_statement_group
        else:
            return self.reverse_condition(statement_group)

    def get_reversed_previous_statement(self, previous_statement: List) -> List:
        """ iterate other conditions in strategy and reverse
            them if they are was not not reversed previous """
        not_previous_statement = []
        for statement in previous_statement:
            if 'previous' not in statement:
                not_previous_statement.append(self.reverse_condition_group(statement))
            else:
                not_previous_statement.append(statement)
        return not_previous_statement

    def form_strategies(self, func_data: Dict) -> Dict:
        # TODO: need to add strategies for depend_on args - when arg match to expected value and when not
        s = []
        if not func_data.get('ifs'):
            s.append(StrategyAny())
        else:
            for num, condition in enumerate(func_data['ifs']):
                # for every next if after if with 0 number we add rule not previous rule
                if num != 0:
                    previous_statement = func_data['ifs'][num - 1]
                    condition += self.get_reversed_previous_statement(previous_statement)
                s.append(condition)
            # now add last strategy, that exclude all previous strategies
            s.append(self.get_reversed_previous_statement(s[-1]))
        func_data['s'] = s

        if len(func_data['return']) < len(func_data['s']):
            for _ in range(len(func_data['s']) - len(func_data['return'])):
                func_data['return'].append({'result': None})
        return func_data

    def get_attr_call_line(self, node: _ast.Attribute) -> Text:
        line = self.source[node.lineno-1][node.col_offset:]
        _call = ''
        # line after attr
        split_by_attr = line.split(node.attr)[1]
        if split_by_attr.startswith('.'):
            _call = split_by_attr.split(',')[0]
        attr_call = node.attr + _call
        return attr_call

    def identify_type_by_attr(self, inner_function_arg: Union[Dict, Any],
                              func: Dict, variables: List, variables_names: Dict) -> None:
        # arg - l_value for attrib in function
        # TODO: add check for args in variables, split method
        import jedi
        from jedi.api.completion import get_signature_param_names
        arg = func['l_value']['args']
        arg_type = None
        if arg in self.func_data['args']:
            func_arg_type = self.func_data['args'][arg].get('type', None)
            if func_arg_type:
                if isinstance(func_arg_type, dict):
                    if not func_arg_type:
                        arg_type = func_arg_type
                else:
                    arg_type = func_arg_type
        attrib = func["attr"]
        if not arg_type:
            arg_type = self.set_type_by_attrib(arg, attrib=attrib)
        init_arg_line = f'{arg} = {arg_type.__name__}(); '
        # get method complition
        line = f'{init_arg_line}{arg}.' + attrib
        line = line[:-1]
        script = jedi.Script(line)
        completions = script.complete(1, len(line))
        # get params names
        first_param = [x for x in get_signature_param_names([completions[0]])][0]
        line = line.split('.')[0] + '.' + completions[0].name + '(' + str(first_param.get_public_name())
        line = line[:-1]
        script = jedi.Script(line)
        # get paramas details - types
        completions = script.complete(1, len(line))
        split_line = jedi_param_type_line.format(param_name=first_param.get_public_name()[:-1])
        split_description = completions[0].description.split(split_line)
        complete_type = split_description[1]
        self.set_type_to_func_args(inner_function_arg, complete_type)
        self.set_dependency_to_arg(inner_function_arg, arg)

    def set_dependency_to_arg(self, arg: Text, dependency_arg: Text):
        """
        :param arg:
        :param dependency_arg:
        :return:
        """
        # TODO: dependency can be different types  - must be a part of (for strings), must include, must be a index of
        #      and etc.
        self.func_data['args'][arg]['depend_on'] = dependency_arg

    def set_type_by_attrib(self, arg_name: Union[Text, Dict], attrib: Text, _slice: Union[Text, int] = None):
        for _type in meta.stnd_types:
            if getattr(_type, attrib, None):
                return self.set_type_to_func_args(arg_name, _type)

    def get_function_args(self, body_item: _ast.Name):
        args = OrderedDict()
        for arg in body_item.args.args:
            if arg.annotation:
                if 'value' in arg.annotation.__dict__:
                    type_arg = arg.annotation.value.id
                else:
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
                class_dict['args'].append((var, value))
            if not isinstance(body_item, ast.FunctionDef):
                continue

            args = self.get_function_args(body_item)
            defaults = []
            for item in body_item.args.defaults:
                if isinstance(item, _ast.Str):
                    defaults.append(item.s)
                elif isinstance(item, _ast.Num):
                    defaults.append(item.n)
                else:
                    defaults.append(item.value)

            if len(args) > len(defaults):
                [defaults.insert(0, 'no_default')
                 for _ in range(len(args) - len(defaults))]
            for num, arg in enumerate(args):
                args[arg]['default'] = defaults[num]

            funct_info = self.visit_FunctionDef(body_item, class_=True)
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
        :param body_item:
        """
        # TODO: need change this to jedi
        doc = ast.get_docstring(body_item)
        doc_types = None
        if not doc or 'type' not in doc:
            doc_types = None
        else:
            for arg in body_item.args.args:
                print('type', arg.arg, doc.split(arg.arg))
        return doc_types

    def report(self) -> None:
        pprint(self.tree)
