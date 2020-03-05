# DO NOT RUN TESTS GENERATION, THIS CASES DOES NOT HASE WORK AROUN YET
import time


def function_with_while_true():
    while True:
        time.sleep(1)


# TODO: not correct code - must be work arounded valid
def function_with_args_modifications_with_function(arg_1):
    arg_1 *= arg_1.split()
    return arg_1