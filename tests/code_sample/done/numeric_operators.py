def int_math_operations():
    a = 13457   # assign int
    b = 167890  # assign int
    c = a*b  # multiply
    d = c**2  # power
    e = c % 120  # mod
    f = +d/e  # truediv
    g = -b  # negative
    result = (((a + b) - f) // 45) * g  # floor div + multiply binary operations
    return result


# TODO: operator.matmul(a, b) goes to numpy tests
def float_math_operations():
    a = 13.457   # assign float
    b = 16.7890  # assign float
    c = a*b  # multiply
    d = c**2.3  # power
    e = c % 1.20  # mod
    f = d/e  # truediv
    g = -b  # negative
    result = (((a + b) - f) // 45) * g  # floor div + multiply binary operations
    return result


def int_bitwise_operations():
    a = -134  # assign int
    b = 167  # assign int
    j = b << b  # Bitwise left shift
    c = a >> b  # Bitwise right shift
    d = ~a  # Bitwise NOT
    e = b | c  # Bitwise OR
    f = d & e  # Bitwise AND
    g = b ^ a  # Bitwise XOR
    return j, c, d, e, f, g
