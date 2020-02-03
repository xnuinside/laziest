def function_no_body(arg1, arg2, arg3):
	pass


def function_with_return_one_arg(arg1, arg2, arg3):
	return arg1


def function_with_return_several_args(arg1, arg2, arg3):
	return arg1, arg2, arg3


def function_with_binary_op_on_several_args(arg1, arg2, arg3):
	return arg1 * arg2 + arg3


def function_with_binary_op_on_several_args_and_tuple_return(arg1, arg2, arg3):
	var = 'one'
	return arg1 * arg2 + arg3, var


def function_with_binary_op_on_several_args_and_tuple_return_multiple_BinOps(arg1, arg2, arg3):
	var = 'one'
	return arg1 * arg2 + arg3, var * arg1

def funct_with_multiple_alias(arg1, arg2, arg3):
	var = 'one'
	alias = var
	return arg1 * arg2 + arg3, var * arg1 * alias