from laziest.params import generate_params_based_on_types
from laziest import analyzer
from copy import deepcopy
from laziest.ast_meta import operators

normal_types = [int, str, list, dict, tuple, set, bytearray, bytes]


def return_assert_value(func_data):
    """
        TODO: need to fix structure to one view. In some cases args come with result pack in some no
    :param func_data:
    :return:
    """
    # null_param - None values dict for each function argument, if exist
    # base_param_strategy - default if no any conditions/limits
    pack_param_strategy, null_param = {}, {}
    random_values = None
    if func_data['args']:
        null_param = {a: None for a in func_data['args']}
        if not func_data.get('ifs', None):
            # if no ifs statements
            pack_param_strategy = generate_params_based_on_types(null_param, func_data)
            # get result for this strategy
            _return_value = get_assert_for_params(func_data, pack_param_strategy)
    if not func_data['return']:
        # if function with 'pass' or without return statement
        func_data['return'] = [{'args': {}, 'result': None}]
    for return_pack in func_data['return']:
        # get for each return statement param strategy and result
        # if err_message - we have error as result
        err_message = None
        args = return_pack.get('args') or pack_param_strategy
        _return_value = return_pack['result']
        if isinstance(return_pack['result'], tuple):
            # if we have tuple as result
            pack_result = None
            result_value = []
            for elem in return_pack['result']:
                if getattr(elem, '__iter__', None) and 'BinOp' in elem:
                    if func_data.get('ifs'):
                        pack_param_strategy = generate_params_based_on_types(null_param,
                                                                             func_data, func_data.get('ifs'),
                                                                             return_pack)
                    pack_result = get_assert_for_params(func_data, pack_param_strategy)
                    args.update(pack_result['args'])
                    if 'error' in pack_result['result']:
                        # if we have exception
                        _return_value = pack_result['result']['error']
                        err_message = pack_result['result']['comment']
                        result_value.append(_return_value)
                    else:
                        result_value.append(pack_result['result'])
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
            print(_return_value)
        elif isinstance(return_pack['result'], dict) and 'BinOp' in return_pack['result']:
            # 'args': bin_op_args or params, 'result': return_value

            if func_data.get('ifs', None):
                pack_param_strategy = generate_params_based_on_types(
                    null_param, func_data, func_data.get('ifs', None), return_pack['result'])
                pack_result = get_assert_for_params(func_data, pack_param_strategy)
            else:
                pack_result = get_assert_for_params(func_data, args)
            args = pack_result['args']
            _return_value = eval_binop_with_params(return_pack['result'], args, args)
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
                    _return_value = args[_args]
                else:
                    _return_value = return_pack['result']
            else:
                random_values = []
                for key, value in return_pack['result'].items():
                    # in dict we can have as values - binop, evals and etc. this can be anything
                    if isinstance(value, dict) and 'l_value' in value:
                        eval_result, random_value = check_eval_result(value, func_data)
                        if eval_result:
                            return_pack['result'][key] = eval_result
                        elif random_value:
                            # mean eval return each time different values, so we see functions like uuid.uuid4().hex
                            # and to check output we need use different checks, like for example, that key in dict
                            # and value not None
                            random_values.append(key)
                    elif isinstance(value, dict) and 'BinOp' in value:
                        # mean we need execute BinOp
                        if isinstance(value['left'], dict) and 'arg' in value['left']:
                            if 'args' in value['left']['arg']:
                                left = f"{value['left']['arg']['args']}[\'{value['left']['slice']}\']"
                            else:
                                left = f"{value['left']['arg']}[\'{value['left']['slice']}\']"
                        else:
                            left = value['left']
                        if isinstance(value['right'], dict) and 'arg' in value['right']:
                            if 'args' in value['right']['arg']:
                                right = f"{value['right']['arg']['args']}[\'{value['right']['slice']}\']"
                            else:
                                right = f"{value['right']['arg']}[\'{value['right']['slice']}\']"
                        else:
                            right = value['right']
                        print(args)
                        try:
                            return_pack['result'][key] = eval(
                                f'{left}{operators[value["op"].__class__]}{right}', deepcopy(args))
                        except KeyError as e:
                            return_pack['result'] = {'error': e.__class__.__name__, 'comment': e}

                _return_value = return_pack['result']
        else:
            if isinstance(return_pack['result'], dict) and 'args' in return_pack['result']:
                return_pack['result'] = args[return_pack['result']['args']]

        yield args, _return_value, err_message, return_pack.get('log', False), random_values


def check_eval_result(statement, func_data):
    """
        sample statements = {'l_value': {'func': {'l_value': {'value': 'uuid',
            't': 'import'}, 'attr': 'uuid4'}, 'args': []}, 'attr': 'hex'}

    :param statement:
    :param func_data:
    :return:
    """
    eval_result = None
    random_values = []
    _import = None
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
                elif 'func' in _statement:
                    _statement['func']['attr'] = _statement['func']['attr'] + '()' + '.' + statement.get('attr', '')
                    statement = _statement['func']
                elif 't' in _statement['l_value']:
                    # we found start object
                    _import = _statement['l_value']['value']
                    _statement = _statement['l_value']['value'] + '.' + _statement.get('attr')
        statement = _statement
    results = []
    if _import:
        globals()[_import] = __import__(_import, _import)
        for i in range(0, 2):
            results.append(eval(statement))
    if results[0] != results[1]:
        print('Different ouputs per run')
        random_values = True
    # maybe make sense return len of result if random values
    return eval_result, random_values


def get_assert_for_params(func_data, params):
    return_value = None
    bin_op_args = None
    print(" print(func_data['args'])")
    print(func_data['args'])

    print(func_data)

    return_value = set()
    for return_pack in func_data['return']:
        _result = return_pack.get('result', {})
        if isinstance(_result, tuple):
            bin_op_args = {}
            result = []
            for num, elem in enumerate(return_pack['result']):
                if isinstance(return_pack['result'][num], dict):
                    print("return_pack['result'][num]")
                    print(return_pack['result'][num])
                    if 'arg' in return_pack['result'][num]:
                        return_value.add(params[return_pack['result'][num]['arg']])
                    elif 'BinOp' in return_pack['result'][num]:
                        return_pack['BinOp'] = True
                        # update binops_arg per tuple with common generated args for function
                        params_ = return_pack['result'][num].get('binop_args', {})
                        params_.update(params)
                        if isinstance(return_pack['result'][num]['BinOp'], bool):
                            bin_op = return_pack['result'][num]
                        else:
                            bin_op = return_pack['result'][num]['BinOp']

                        eval_result = eval_binop_with_params(bin_op, params_, params_)
                        print(eval_result)
                        if isinstance(eval_result, dict) and 'error' in eval_result:
                            result = eval_result
                            break
                        else:
                            result.append(eval_result)
                    else:
                        result.append(elem)
                elif type(return_pack['result'][num] in normal_types):
                    result.append(return_pack['result'][num])
                else:
                    result.append(_result)
            print(return_value)
            if isinstance(result, list):
                return_value = tuple(result)
            else:
                return_value = result
        elif isinstance(_result, dict) and 'BinOp' in _result:
            # update binops_arg per tuple with common generated args for function
            params_ = return_pack['result'].get('binop_args', {})
            params_.update(params)
            if isinstance(return_pack['result']['BinOp'], bool):
                bin_op = return_pack['result']
            else:
                bin_op = return_pack['result']['BinOp']
            return_pack['result'] = eval_binop_with_params(bin_op, params_, params_)
        elif isinstance(_result, dict) and 'args' in _result:
            params = _result['args']
        elif _result is None:
            return_value = None
        else:
            return_value = _result

    result = {'args': bin_op_args or params, 'result': return_value}
    return result


def simplify_bin_op(bin_op, eval_params, params):
    """
        eval each side of BinOp, simplify nested BinOp statements by step-by-step evalution
    :param bin_op:
    :param eval_params:
    :param params:
    :return:
    """
    for item in ['left', 'right']:
        if isinstance(bin_op[item], dict):
            try:
                if 'BinOp' in bin_op[item]:
                    bin_op[item] = eval_binop_with_params(bin_op[item], eval_params, params)
                    if isinstance(bin_op[item], dict) and 'error' in bin_op[item]:
                        print(bin_op)
                        return bin_op[item]
                elif 'args' in bin_op[item]:
                    bin_op[item] = params[bin_op[item]['args']]
                elif 'arg' in bin_op[item] and 'slice' in bin_op[item]:
                    bin_op[item] = bin_op[item]['arg'][bin_op[item]['slice']]
            except KeyError as e:
                return_value = {'error': e.__class__.__name__, 'comment': e}
                return return_value


def eval_binop_with_params(bin_op, eval_params, params):
    """
        eval BinOp with params to get result
    :param bin_op:
    :param eval_params:
    :param params:
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
        if bin_op['left'] not in params:
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
