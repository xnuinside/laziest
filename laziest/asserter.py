from laziest.params import generate_params_based_on_types
from laziest import analyzer
from copy import deepcopy


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
    if func_data['args']:
        null_param = {a: None for a in func_data['args']}
        if not func_data.get('ifs', None):
            # if no ifs statements
            pack_param_strategy = generate_params_based_on_types(null_param, func_data['args'])
            # get result for this strategy
            pack_result = get_assert_for_params(func_data, pack_param_strategy)
    for return_pack in func_data['return']:
        # get for each return statement param strategy and result
        # if err_message - we have error as result
        err_message = None
        args = return_pack['args']
        if isinstance(return_pack['result'], tuple):
            return_value = []
            args = {}
            # if we have tuple as result
            for elem in return_pack['result']:
                if 'BinOp' in elem:
                    pack_param_strategy = generate_params_based_on_types(null_param,
                                                                         func_data['args'], func_data.get('ifs'),
                                                                         return_pack)
                    pack_result = get_assert_for_params(func_data, pack_param_strategy)
                    args.update(pack_result['args'])
                    return_value.append(pack_result['result'])
            return_value = tuple(return_value)
        if 'BinOp' in return_pack:
            # 'args': bin_op_args or params, 'result': return_value
            print('ifsss')
            if func_data.get('ifs', None):
                pack_param_strategy = generate_params_based_on_types(
                    null_param, func_data['args'], func_data['ifs'], return_pack)
                pack_result = get_assert_for_params(func_data, pack_param_strategy)

            args = pack_result['args']
            return_value = pack_result['result']
        elif not args:
            args = pack_param_strategy
        elif isinstance(return_pack['result'], dict) and 'error' in return_pack['result']:
            # if we have exception
            return_value = return_pack['result']['error']
            err_message = return_pack['result']['comment']
        else:

            if isinstance(return_pack['result'], dict) and 'args' in return_pack['result']:

                return_pack['result'] = args[return_pack['result']['args']]
        return_value = return_pack['result']
        yield args, return_value, err_message, return_pack.get('log', False)


def get_assert_for_params(func_data, params):
    return_value = None
    bin_op_args = None
    args_names = [arg[0] for arg in func_data['args']]
    print(args_names)
    for return_pack in func_data['return']:
        result = return_pack.get('result', {})
        if isinstance(result, tuple):
            return_value = []
            bin_op_args = {}
            print('here?')
            for num, _ in enumerate(return_pack['result']):
                print(type(return_pack['result'][num]))
                if isinstance(return_pack['result'][num], dict):

                    print('here2')
                    if 'arg' in return_pack['result'][num]:
                        return_value.append(params[return_pack['result'][num]['arg']])
                    elif 'BinOp' in return_pack['result'][num]:
                        return_pack['BinOp'] = True
                        # update binops_arg per tuple with common generated args for function
                        params_ = return_pack['result'][num].get('binop_args', {})
                        params_.update(params)
                        result = eval_binop_with_params(return_pack['result'][num]['BinOp'], params_, params_)
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
            # update binops_arg per tuple with common generated args for function
            params_ = return_pack['result'].get('binop_args', {})
            params_.update(params)
            return_value = eval_binop_with_params(return_pack['result']['BinOp'], params_, params_)
        elif isinstance(result, dict) and 'args' in result:
            params = result['args']
        elif result is None:
            return_value = None
        else:
            return_value = result
    result = {'args': bin_op_args or params, 'result': return_value}
    return result


def eval_binop_with_params(bin_op, eval_params, params):
    """
        eval binop with params to get result
    :param bin_op:
    :param eval_params:
    :param params:
    :return:
    """
    eval_params.update(params)
    try:
        # deepcopy need to avoid insert global params in eval_params dict
        return_value = eval(bin_op, deepcopy(eval_params))
        print(return_value)
        print('BinOppp')

    except Exception as e:
        analyzer.pytest_needed = True
        return_value = {'error': e.__class__.__name__, 'comment': e}
    return return_value