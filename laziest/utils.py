from typing import Union, Dict, Any


def get_value_name(value: Union[Dict, Any], separate_slice=False) -> Any:
    """

    :param value: can be dict, dict with 'args' key - mean this is {'arg': {'args': 'product_quantity'}, 'slice': 1}
            or {'arg': 'product_quantity', 'slice': 1} or 'product_quantity'
    :param value: separate_slice
    :return:
    """
    print(value)
    if isinstance(value, dict) and 'arg' in value:

        if 'args' in value['arg']:
            args = value['arg']['args']
        else:
            args = value['arg']
    else:
        args = value['args']
    print(args)
    if not separate_slice:
        if 'slice' in value:
            args = f"{args}[\'{value['slice']}\']" if isinstance(value['slice'], str) \
                else f"{args}[{value['slice']}]"
        return args, None
    else:
        _slice = value.get('slice', None)
        return args, _slice


def is_int(value):
    try:
        return int(value)
    except Exception as e:
        raise e
        return False
