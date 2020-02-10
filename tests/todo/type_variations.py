# --- without
def validate_package_weight_trivial(weight):
    if weight <= 0:
        raise Exception("Weight of package cannot be 0 or below")
    else:
        if weight > 200:
            return False
        elif weight < 200:
            return True


class CustomException(Exception):
    pass


# --- with CustomException
def validate_package_weight_custom_error(weight):
    if weight <= 0:
        raise CustomException("Weight of package cannot be 0 or below")
    else:
        if weight > 200:
            return False
        elif weight < 200:
            return True


# --- with CustomException
def validate_package_weight_normal_code(weight):
    if weight <= 0:
        raise CustomException("Weight of package cannot be 0 or below")
    elif weight > 200:
        return False
    else:
        return True


def validate_package_weight_short_code(weight):
    if weight <= 0:
        raise CustomException("Weight of package cannot be 0 or below")
    return not (weight > 200)


def validate_package_weight_normal_code_types_in_doc(weight):
    """

    :param weight: weight of mail package, that we need to validate
    :type weight: int
    :return: if package weight > 200 - return False (we cannot deliver this package)
    """
    if weight <= 0:
        raise CustomException("Weight of package cannot be 0 or below")
    elif weight > 200:
        return False
    else:
        return True


def validate_package_weight_normal_code_types_in_doc_no_type(weight):
    """

    :param weight: weight of mail package, that we need to validate, type int
    :return: if package weight > 200 - return False (we cannot deliver this package)
    """
    if weight <= 0:
        raise CustomException("Weight of package cannot be 0 or below")
    elif weight > 200:
        return False
    else:
        return True


def validate_package_weight_normal_code_type_annotation(weight: int) -> bool:
    """
    :param weight: weight of mail package, that we need to validate
    :return: if package weight > 200 - return False (we cannot deliver this package)
    """
    if weight <= 0:
        raise CustomException("Weight of package cannot be 0 or below")
    elif weight > 200:
        return False
    else:
        return True
