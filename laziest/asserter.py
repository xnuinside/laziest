from laziest.params import generate_params_based_on_types
from laziest import analyzer
normal_types = [int, str, list, dict, tuple, set, bytearray, bytes]


def return_assert_value(func_data):
    if not func_data['return']:
        func_data['return'] = [{'args': (), 'result': None}]
    params = {}
    if func_data['args']:
        # func_definition = s.pytest_parametrize_decorator + func_definition
        # params structure (1-params values, last 'assert' - assert value)
        null_param = {a: None for a in func_data['args']}
        #if class_method_type != 'static':
            #func_data['args'] = {x: func_data['args'][x] for x in deepcopy(null_param)
                                 #if x not in reserved_words}
            #null_param = {x: null_param[x]
                          #for x in null_param if x not in reserved_words}
        params = generate_params_based_on_types(null_param, func_data['args'])
        params_assert = get_assert_for_params(func_data, params)
    for return_pack in func_data['return']:
        comment = None
        print(return_pack)
        print("func_data['return']")
        print(func_data['return'])
        args = return_pack['args']
        if not args:
            args = params
        if 'BinOp' in return_pack:
            return_pack = params_assert
        if isinstance(return_pack['result'], dict) and 'error' in return_pack['result']:
            # if we have exception
            return_value = return_pack['result']['error']
            comment = return_pack['result']['comment']
        else:

            if isinstance(return_pack['result'], dict)  and 'args' in return_pack['result']:

                return_pack['result'] = args[return_pack['result']['args']]
            return_value = return_pack['result']
        yield args, return_value, comment, return_pack.get('log', False)


def get_assert_for_params(func_data, params):
    return_value = None
    for return_pack in func_data['return']:
        result = return_pack.get('result', {})
        if isinstance(result, tuple):
            return_value = []
            for num, _ in enumerate(return_pack['result']):
                if isinstance(return_pack['result'][num], dict):
                    if 'arg' in return_pack['result'][num]:
                        print(return_pack['result'])
                        print('returnnn')
                        return_value.append(params[return_pack['result'][num]['arg']])
                    elif 'BinOp' in return_pack['result'][num]:
                        return_pack['BinOp'] = True
                        result = eval_binop_with_params(return_pack['result'][num]['BinOp'],
                            return_pack['result'][num].get('binop_args', {}),
                            params)
                        if isinstance(result, dict) and 'error' in result:
                            return_value = result
                            break
                        else:
                            return_value.append(result)
                elif type(return_pack['result'][num] in normal_types):
                    return_value.append(return_pack['result'][num])
            if isinstance(return_value, list):
                return_value = tuple(return_value)
        elif isinstance(result, dict) and 'BinOp' in result:

            return_pack['BinOp'] = True
            return_value = eval_binop_with_params(return_pack['result']['BinOp'], return_pack['result'].get(
                'binop_args', {}), params)
        elif isinstance(result, dict) and 'args' in result:
            params = result['args']
        elif result is None:
            return_value = None
        else:
            print('return')
            print(func_data)
            print(func_data['return'])
            return_value = result
    print({'args': params, 'result': return_value})
    return {'args': params, 'result': return_value}


def eval_binop_with_params(bin_op, global_params, params):
    """
        eval binop with params to get result
    :param bin_op:
    :param global_params:
    :param params:
    :return:
    """
    global_params.update(params)
    try:

        return_value = eval(bin_op, global_params)
        print(return_value)
        print('BinOppp')

    except Exception as e:
        analyzer.pytest_needed = True
        return_value = {'error': e.__class__.__name__, 'comment': e}
    return return_value
