
def return_assert_value(func_data):
    comment = None
    if not func_data['return']:
        func_data['return'] = [{'args': (), 'result': None}]
    for return_pack in func_data['return']:
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
