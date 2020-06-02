def epydoc_type_in_doc(weight):
    """
        @type weight: int
    """
    if weight <= 0:
        raise Exception("Weight of package cannot be 0 or below")
    elif weight > 200:
        return False
    else:
        return True


def sphinx_type_in_doc(weight):
    """
    :type weight: int
    :param weight: weight of mail package, that we need to validate, type int
    :return: if package weight > 200 - return False (we cannot deliver this package)
    """
    if weight <= 0:
        raise Exception("Weight of package cannot be 0 or below")
    elif weight > 200:
        return False
    else:
        return True


def numpy_type_in_doc(weight):
    """
    weight : int
        Array_like means all those objects -- lists, nested lists,
        etc. -- that can be converted to an array. We can also
        refer to variables like `var1`."""
    if weight <= 0:
        raise Exception("Weight of package cannot be 0 or below")
    elif weight > 200:
        return False
    else:
        return True


def epydoc_type_in_doc(weight):
    """
        @type weight: int
    """
    if weight <= 0:
        raise Exception("Weight of package cannot be 0 or below")
    elif weight > 200:
        return False
    else:
        return True


def sphinx_type_in_doc(weight):
    """
    :type weight: int
    :param weight: weight of mail package, that we need to validate, type int
    :return: if package weight > 200 - return False (we cannot deliver this package)
    """
    if weight <= 0:
        raise Exception("Weight of package cannot be 0 or below")
    elif weight > 200:
        return False
    else:
        return True


def numpy_type_in_doc_dict(peoples):
    """
    weight : array_like
        Array_like means all those objects -- lists, nested lists,
        etc. -- that can be converted to an array. We can also
        refer to variables like `var1`."""
    return peoples[1]



