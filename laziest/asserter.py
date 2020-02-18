
from copy import deepcopy
from typing import Tuple, Union, Any, Dict, List
from laziest.params import generate_params_based_on_strategy
from laziest import analyzer
from laziest.ast_meta import operators
from laziest.utils import is_int

normal_types = [int, str, list, dict, tuple, set, bytearray, bytes]


class StrategyAny:
    pass


def reverse_condition(statement: Dict) -> Dict:

    # todo: need to move it
    ops_pairs = {
        '==': '!=',
        '>': '<=',
        '>=': '<',
        '!=': '==',
        '<=': '>',
        '<': '>=',
        'not': '',
        '': 'not'
    }
    not_statement = deepcopy(statement)
    # change to opposite in pair != to == > to <= and etc
    not_statement['ops'] = ops_pairs[not_statement['ops']]
    not_statement['previous'] = True
    return not_statement


def get_reversed_previous_statement(previous_statement: List) -> List:
    """ iterate other conditions in strategy and reverse
        them if they are was not not reversed previous """
    not_previous_statement = []
    for statement in previous_statement:
        if 'previous' not in statement:
            not_previous_statement.append(reverse_condition(statement))
        else:
            not_previous_statement.append((statement))
    return not_previous_statement


def form_strategies(func_data: Dict):
    # todo: need to move it on analyzer with refactoring
    s = []
    if not func_data.get('ifs'):
        s.append(StrategyAny())
    else:
        for num, condition in enumerate(func_data['ifs']):
            # for every next if after if with 0 number we add rule not previous rule
            if num != 0:
                previous_statement = func_data['ifs'][num - 1]
                condition += get_reversed_previous_statement(previous_statement)
            s.append(condition)
        # now add last strategy, that exclude all previous strategies
        s.append(get_reversed_previous_statement(s[-1]))
    func_data['s'] = s
    return func_data


def resolve_strategy(return_pack: Dict, func_data: Dict, strategy: Dict, base_params: Dict):
    # TODO: split this method on small functions, very long

    args = return_pack.get('args', {})
    null_param = {}
    err_message = None
    random_values = None
    log = return_pack.get('log', None)
    if isinstance(strategy, StrategyAny):
        # mean we have no conditionals to args
        pack_param_strategy = generate_params_based_on_strategy(null_param, func_data)
        _return_value = return_pack['result']
    else:
        _return_value = return_pack['result']
        pack_param_strategy = generate_params_based_on_strategy(args,
                                                                func_data,
                                                                strategy,
                                                                base_params)

    if isinstance(return_pack['result'], tuple):
        # if we have tuple as result
        pack_result = None
        result_value = []
        for elem in return_pack['result']:
            if getattr(elem, '__iter__', None) and 'BinOp' in elem:
                # TODO: strange if
                pack_result = get_assert_for_params(return_pack, pack_param_strategy)['result']

                if 'error' in pack_result:
                    # if we have exception
                    _return_value = pack_result['error']
                    err_message = pack_result['comment']
                    result_value.append(_return_value)
                else:
                    result_value.append(pack_result)
                break
            else:
                if not pack_result and isinstance(elem, dict) and 'args' in elem:
                    result_value.append(pack_param_strategy[elem['args']])
                else:
                    result_value.append(elem)
        if len(result_value) == 1:
            _return_value = result_value[0]
        else:
            _return_value = tuple(result_value)
    elif isinstance(return_pack['result'], dict) and 'BinOp' in return_pack['result']:
        # 'args': bin_op_args or params, 'result': return_value
        _return_value = eval_bin_op_with_params(return_pack['result'], pack_param_strategy, pack_param_strategy)
        if isinstance(_return_value, dict) and 'error' in _return_value:
            err_message = _return_value['comment']
            _return_value = _return_value['error']
    elif isinstance(return_pack['result'], dict):
        if 'error' in return_pack['result']:
            # if we have exception
            _return_value = return_pack['result']['error']
            err_message = return_pack['result']['comment']

        elif return_pack.get('args') or return_pack['result'].get('args'):
            _args = return_pack['result'].get('args') or return_pack['result'].get('binop_args')
            if _args:
                _return_value = pack_param_strategy[_args]
            else:
                _return_value = return_pack['result']
        else:
            random_values = []
            if len(list(return_pack['result'].keys())) == 2 and 'func' in return_pack['result'] \
                    and 'args' in return_pack['result']:
                eval_result, random_value = run_function_several_times(
                    return_pack['result'], func_data, pack_param_strategy)
                if eval_result:
                    return_pack['result'] = eval_result
                elif random_value:
                    # mean eval return each time different values, so we see functions like uuid.uuid4().hex
                    # and to check output we need use different checks, like for example, that key in dict
                    # and value not None
                    random_values.append(return_pack['result'])
            else:
                for key, value in return_pack['result'].items():
                    # in dict we can have as values - binop, evals and etc. this can be anything
                    if isinstance(value, dict) and 'l_value' in value:
                        eval_result, random_value = run_function_several_times(value, func_data, pack_param_strategy)
                        if eval_result:
                            return_pack['result'][key] = eval_result
                        elif random_value:
                            # mean eval return each time different values, so we see functions like uuid.uuid4().hex
                            # and to check output we need use different checks, like for example, that key in dict
                            # and value not None
                            random_values.append(key)
                    elif isinstance(value, dict) and 'BinOp' in value:
                        # mean we need execute BinOp
                        try:
                            return_pack['result'][key] = eval_bin_op_with_params(
                                value, pack_param_strategy, pack_param_strategy)
                        except KeyError as e:
                            return_pack['result'] = {'error': e.__class__.__name__, 'comment': e}

            _return_value = return_pack['result']
    else:
        if isinstance(return_pack['result'], dict) and 'args' in return_pack['result']:
            _return_value = args[return_pack['result']['args']]

    return pack_param_strategy, _return_value, err_message, log, random_values


def return_assert_value(func_data: Dict):
    """
        TODO: need to fix structure to one view. In some cases args come with result pack in some no
    :param func_data:
    :return:
    """
    # null_param - None values dict for each function argument, if exist
    # base_param_strategy - default if no any conditions/limits
    # each result pack == strategy, in ideal need to move it in return pack args
    func_data = form_strategies(func_data)

    base_params = generate_params_based_on_strategy({}, func_data)
    if not func_data['return']:
        # if function with 'pass' or without return statement
        func_data['return'] = [{'args': {}, 'result': None}]
    for num, return_pack in enumerate(func_data['return']):
        # get for each return statement param strategy and result
        # if err_message - we have error as result
        # take args strategy for this return
        strategy = func_data['s'][num]

        args, _return_value, err_message, log, random_values = resolve_strategy(
            return_pack, func_data, strategy, base_params)

        yield args, _return_value, err_message, log, random_values


def run_function_several_times(statement: Dict, func_data: Dict, pack_param_strategy: Dict):
    """
        we want to understand does function produce random result or not
        sample statements = {'l_value': {'func': {'l_value': {'value': 'uuid',
            't': 'import'}, 'attr': 'uuid4'}, 'args': []}, 'attr': 'hex'}

    :param statement:
    :param func_data:
    :param pack_param_strategy:
    :return:
    """
    eval_result = None
    random_values = []
    _import = None
    # TODO: need split this code and remove statement
    while isinstance(statement, dict):
        if not isinstance(statement.get('value', {}), dict):
            _load = func_data[statement['t']].get(statement['value'])
            if statement['t'] == 'import':
                if _load in globals()['__builtin__']:
                    raise
        for key in ['l_value', 'func']:
            if key in statement:
                _statement = statement[key]
                if 'l_value' in _statement and 'attr' in _statement['l_value']:
                    _statement['l_value']['attr'] = _statement['l_value']['attr'] + '.' + statement.get('attr', '')
                    _statement = _statement['l_value']
                if 'l_value' in _statement and 'args' in _statement['l_value']:
                    _statement = _statement['l_value']['args'] + '.' + _statement.get('attr')
                elif 'func' in _statement:
                    _statement['func']['attr'] = _statement['func']['attr'] + '()' + '.' + statement.get('attr', '')
                    statement = _statement['func']
                elif 'l_value' not in _statement:
                    _statement = f'{_statement["args"]}.{statement["attr"]}'
                elif 't' in _statement['l_value']:
                    # we found start object
                    _import = _statement['l_value']['value']
                    _statement = _statement['l_value']['value'] + '.' + _statement.get('attr')
        statement = _statement

    results = []
    if _import:
        globals()[_import] = __import__(_import, _import)
    for i in range(0, 2):
        results.append(eval(statement, globals().update(deepcopy(pack_param_strategy))))
    if results[0] != results[1]:
        print('Different outputs per run')
        random_values = True
    # maybe make sense return len of result if random values
    if not random_values:
        eval_result = results[0]
    return eval_result, random_values


def resolve_bin_op_in_result(return_pack: Dict, params: Dict):
    if not return_pack.get('BinOp'):
        return_pack['BinOp'] = True
    # update binops_arg per tuple with common generated args for function
    params_ = return_pack.get('binop_args', {})
    params_.update(params)
    if isinstance(return_pack['BinOp'], bool):
        bin_op = return_pack
    else:
        bin_op = return_pack['BinOp']
    return eval_bin_op_with_params(bin_op, params_, params_)


def resolve_tuple_in_return(result_tuple: Tuple, params: Dict) -> Union[List, Any]:
    result = []
    for num, elem in enumerate(result_tuple):
        if isinstance(result_tuple[num], dict):
            if 'BinOp' in result_tuple[num]:
                # if we have binop as one of the values in tuple
                eval_result = resolve_bin_op_in_result(result_tuple[num], params)
                if isinstance(eval_result, dict) and 'error' in eval_result:
                    result = eval_result
                    break
                else:
                    result.append(eval_result)
            else:
                result.append(elem)
        elif type(result_tuple[num] in normal_types):
            result.append(result_tuple[num])
        else:
            result.append(result_tuple[num])
    return result


def get_assert_for_params(return_pack: Dict, params: Dict):

    bin_op_args = None
    return_value = return_pack.get('result', {})

    _result = return_pack.get('result', {})
    if isinstance(_result, tuple):
        result = resolve_tuple_in_return(return_pack['result'], params)
        if isinstance(result, list):
            return_value = tuple(result)
        else:
            return_value = result
    elif isinstance(_result, dict) and 'BinOp' in _result:
        # update binops_arg per tuple with common generated args for function
        return_value = resolve_bin_op_in_result(return_pack['result'], params)
    elif isinstance(_result, dict) and 'args' in _result:
        params = _result['args']
    else:
        return_value = _result
        args = return_pack.get('args', {})
        del_keys = []
        new_args = deepcopy(args)
        for key, value in args.items():
            if '[' in key:
                arg = key.split('[')[0]
                _slice = key.split('[')[1].split(']')[0]
                new_args[arg] = params[arg]
                int_slice = is_int(_slice)
                if not int_slice:
                    new_args[arg][_slice] = value
                else:
                    new_args[arg].insert(int_slice, value)
                del_keys.append(key)

        for _key in del_keys:
            del new_args[_key]
        for arg in params:
            if arg not in new_args:
                new_args[arg] = params[arg]
        return_pack['args'] = new_args

    args = bin_op_args or params
    result = {'args': args, 'result': return_value}
    return result


def simplify_bin_op(bin_op: Dict, eval_params: Dict, params: Dict) -> Dict:
    """
        eval each side of BinOp, simplify nested BinOp statements by step-by-step execution
    :param bin_op:
    :param eval_params:
    :param params:
    :return:
    """
    for item in ['left', 'right']:
        if isinstance(bin_op[item], dict):
            try:
                if 'BinOp' in bin_op[item]:
                    bin_op[item] = eval_bin_op_with_params(bin_op[item], eval_params, params)
                    if isinstance(bin_op[item], dict) and 'error' in bin_op[item]:
                        return bin_op[item]
                elif 'args' in bin_op[item]:
                    bin_op[item] = params[bin_op[item]['args']]
                elif 'arg' in bin_op[item] and 'slice' in bin_op[item]:
                    if bin_op[item]['arg'].get('args'):
                        bin_op[item] = params[bin_op[item]['arg']['args']][bin_op[item]['slice']]
                    else:
                        _slice = bin_op[item]['slice']
                        if isinstance(bin_op[item]['arg'], dict):
                            # dicts that defined in variables will come like
                            # {'arg': {'num': 2, 'value_two': 5}, 'slice': 'num'}
                            bin_op[item] = bin_op[item]['arg'][_slice]

                        else:
                            bin_op[item] = params[bin_op[item]['arg']].get(_slice)

            except KeyError as e:
                return_value = {'error': e.__class__.__name__, 'comment': e}
                return return_value


def eval_bin_op_with_params(bin_op: Dict, eval_params: Dict, params: Dict) -> Union[Any, Dict]:

    """
        eval BinOp with params to get result
    :param bin_op:
    :param eval_params: can contain imports of standard modules if needed in eval
    :param params: arguments and variables that used in BinOp
    :return:
    """
    eval_params.update(params)
    if isinstance(bin_op, dict):
        if 'error' in bin_op:
            return bin_op
        simplify = simplify_bin_op(bin_op, eval_params, params)
        if simplify:
            return simplify
        if bin_op['left'] not in params:
            left = bin_op['left'] if not isinstance(bin_op['left'], str) else f'\'{bin_op["left"]}\''
        else:
            left = params[bin_op['left']]
        if bin_op['right'] not in params:
            right = bin_op['right'] if not isinstance(bin_op['right'], str) else f'\'{bin_op["right"]}\''
        else:
            right = params[bin_op['right']]
        bin_op = f"{left}{operators[bin_op['op'].__class__]}{right}"
    try:
        # deepcopy need to avoid insert global params in eval_params dict
        return_value = eval(str(bin_op), deepcopy(eval_params))
    except NameError as e:
        # TODO: need to fix unnecessary iteration
        if bin_op in e.args[0]:
            return bin_op
    except Exception as e:
        analyzer.pytest_needed = True
        return_value = {'error': e.__class__.__name__, 'comment': e}
    return return_value
