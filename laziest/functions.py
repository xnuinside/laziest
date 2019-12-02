from typing import Dict, Text
from laziest.params import generate_params_based_on_types
from laziest import strings as s


def get_method_signature(func_name: Text, async_type: bool) -> Text:
    method_signature = s.method_signature if not async_type else s.async_method_signature
    # create test method signature
    func_definition = method_signature.format(SP_4=s.SP_4, method=func_name)
    return func_definition


def test_creation(func_name: Text, func_data: Dict, async_type: bool = False) -> Text:
    """ method to generate test body """
    func_definition = get_method_signature(func_name, async_type)
    if func_data['args']:
        # if we have argument in function
        func_definition = s.pytest_parametrize_decorator + func_definition
        # params structure (1-params values, last 'assert' - assert value)
        null_param = {a: None for a in func_data['args']}
        null_param['assert'] = None
        params = generate_params_based_on_types(null_param, func_data['args'])
        print(params)
        func_definition = func_definition.replace("()", "(params)").replace("[]", str(params))
        args = [a + ", " for a in func_data['args']]

        if func_data['return'] is None:
            # check method correct execution
            func_definition += " == None"
    else:
        if isinstance(func_data['return'], dict) and 'error' in func_data['return']:
            # if we have exception
            print(str(func_data['return']['error'][0]))
            exc_name = str(func_data['return']['error'][0]).split('\'')[1]
            comment = f'{s.SP_4}{s.SP_4}# ' + str(func_data['return']['error'][1])
            func_definition += f" with pytest.raises({exc_name}): \n{comment} \n" \
                 f"{s.SP_4}{s.SP_4}{func_name}()"
        else:
            func_definition += s.assert_string + f' {func_name}() =='
            func_definition += f" \'{func_data['return']}\'" \
                if isinstance(func_data['return'], str) else f" {func_data['return']}"
    func_definition += "\n\n\n"
    return func_definition
