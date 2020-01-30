from laziest.params import generate_params_based_on_types
from laziest import analyzer
normal_types = [int, str, list, dict, tuple, set, bytearray, bytes]


def return_assert_value(func_data):
    comment = None
    if not func_data['return']:
        func_data['return'] = [{'args': (), 'result': None}]
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
        func_data['return'] = params_assert
    for return_pack in func_data['return']:
        print(return_pack)
        print("func_data['return']")
        print(func_data['return'])
        args = return_pack['args']
        if isinstance(return_pack['result'], dict) and 'error' in return_pack['result']:
            # if we have exception
            print(str(return_pack['result']['error'][0]))
            print("comment")
            print(return_pack['result']['error'][0])
            return_value = str(return_pack['result']['error'][0]).split('\'')[1]
            comment = return_pack['result']['error'][1]
        else:
            return_value = return_pack['result']
        yield args, return_value, comment


def get_assert_for_params(func_data, params):
    print('we params')
    print(func_data)
    print(params)
    return_value = None
    for return_pack in func_data['return']:
        if isinstance(return_pack['result'], tuple):
            return_value = []
            for num, _ in enumerate(return_pack['result']):
                if isinstance(return_pack['result'][num], dict):
                    if 'arg' in return_pack['result'][num]:
                        print(return_pack['result'])
                        print('returnnn')
                        return_value.append(params[return_pack['result'][num]['arg']])
                    elif 'BinOp' in return_pack['result'][num]:
                        result = eval_binop_with_params(
                            return_pack['result'][num]['BinOp'],
                            return_pack['result'][num].get('global_vars', {}),
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
        elif isinstance(return_pack['result'], dict) and 'BinOp' in return_pack['result']:
            return_value = eval_binop_with_params(return_pack['result']['BinOp'], return_pack['result'].get(
                'global_vars', {}), params)
        elif isinstance(return_pack['result'], dict) and 'arg' in return_pack['result']:
            print(return_pack)
            print('return_pack')
            return_value = params[return_pack['result']['arg']]
            print(return_value)
        elif return_pack['result'] is None:
            return_value = None
        else:
            print('return')
            print(func_data)
            print(func_data['return'])
            return_value = return_pack['result']
    print('return_value')
    print(return_value)
    print(func_data)
    return [{'args': params, 'result': return_value}]


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
    except Exception as e:
        analyzer.pytest_needed = True
        return_value = {'error': (e.__class__, e,)}
    return return_value
