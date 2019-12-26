def one_condition_standard_exception(arg1):
    if arg1 == '1':
        raise Exception('we hate 1')
    else:
        return arg1


class CustomException(Exception):
    pass


def one_condition_custom_exception(arg1):
    if arg1 == '1':
        raise CustomException('we hate 1')
    else:
        return arg1
