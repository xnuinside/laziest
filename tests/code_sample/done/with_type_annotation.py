from typing import Dict, Text, List


def return_str(arg: str):
    return arg


def return_int(arg: int):
    return arg


def return_float(arg: float):
    return arg


def return_dict(arg: dict):
    return arg


def return_list(arg: list):
    return arg


def return_typing_text(arg: Text):
    return arg


def return_typing_dict(arg: Dict):
    return arg


def return_typing_list(arg: List):
    return arg


def str_action_return(arg: str):
	return "1" + arg


def return_action_dict(arg: dict):
	dict_var = {'num': 2, 'value_two': 5}
	return (arg['num'] * dict_var['value_two'])


def return_action_list(arg: list):
	dict_var = {'num': 2, 'value_two': 5}
	return (arg[1] * dict_var['value_two'])
