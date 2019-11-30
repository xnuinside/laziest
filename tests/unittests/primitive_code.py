def primitive_function():
	pass


def primitive_function_with_constant_return_int():
	return 1


def primitive_function_with_constant_return_float():
	return 1.003


def primitive_function_with_statement_return():
	return (1 * 4) * int('3')


def primitive_function_with_statement_return_based_on_inside_var():
	dict_var = {'num': 2, 'value_two': 5}
	return (dict_var['num'] * dict_var['value_two']) * int('3')


def primitive_function_with_statement_return_based_on_inside_var_with_several_vars():
	dict_var = {'num': 2, 'value_two': 5}
	second_dir = {'int': 23}
	return (dict_var['num'] * dict_var['value_two']) * second_dir['int']


def primitive_function_with_statement_return_based_on_inside_var_with_several_vars_and_name_alias():
	dict_var = {'num': 22, 'value_two': 5}
	second_dir = {'int': 23}
	alias_var = dict_var
	return (dict_var['num'] * alias_var['value_two']) * second_dir['int']


def primitive_function_with_str():
	dict_var = {'num': 'mama', 'value_two': 5}
	second_dir = {'int': '23'}
	alias_var = dict_var
	return (dict_var['num'] * alias_var['value_two']) + second_dir['int']


def primitive_function_with_str_and_type_error():
	dict_var = {'num': 'mama', 'value_two': 5}
	second_dir = {'int': 23}
	alias_var = dict_var
	return (dict_var['num'] * alias_var['value_two']) + second_dir['int']


def primitive_function_with_str_and_atr_error():
	dict_var = {'num': 'mama', 'value_two': 5}
	second_dir = {'int': 23}
	alias_var = dict_var
	return (dict_var['num'] * alias_var['not_exist']) + second_dir['int']