Strategy resolving for arguments
================================


def func():
    pass

0:
   no args

---------------------------

def func(arg1):
    if True:
        pass

strategies:
0:
   any

(function's result does not depend on argument)

---------------------------

def func(arg1):
    if False is True:
        pass
    elif True is True:
        pass


strategies:
0:
   any

(function's result does not depend on argument)

---------------------------

def func(arg1):
    if arg1:
        return arg1

strategies:
0:
    arg1 != None, arg1 != '', arg1 != 0, arg1 != [], arg1 != (), arg1 != {}. arg1 != any_empty iterable object

---------------------------

def func(arg1):
    if arg1 > 2:
        return arg1
    return arg1


strategies:
0:
    int(arg1) > 2 or float(arg1) > 2
1:
    int(arg1) <= 2 or float(arg1) <= 2

---------------------------

def func(arg1, arg2):
    if arg1 > 2:
        return arg1
    elif arg2 == 3:
        return arg1 * 3
    else:
        arg1 += 1
    return arg1, arg2


strategies:
0:
    int(arg1) > 2 or float(arg1) > 2

1:  arg2 == 3, int(arg1) <= 2 or float(arg1) <= 2

2:  arg2 != 3, int(arg1) <= 2 or float(arg1) <= 2

---------------------------

Work with overlap strategies


arg2 < 3 and arg2 < 4 -> mean arg2 < 4

arg1< 5 and arg1 > 2 or arg1 > 7 and arg1 < 12

(2,5) and (7,12)

# statement with opposite conditions in same time
# always be false - need to workaround in Analyser step
a == True and a != True