Laziest
=======

Generator of test_*.py files for your Python code.
Package that trying generate unit tests for you.

In step of testing idea :)

From code like this:

def one_condition_custom_exception_and_return_binary_op_and_key(arg1, arg2, arg3):
    if arg1 == '1':
        raise CustomException('we hate 1')
    elif arg2[3] > 2:
        print(f'{arg2[3]} more when 2')
    var = 1
    alias = var
    return arg1 * arg2[3] + arg3['number'], var * arg1 * alias - 2


Laziest create such test:

def test_one_condition_custom_exception_and_return_binary_op_and_key(capsys):

    assert one_condition_custom_exception_and_return_binary_op_and_key(
        arg1=-720, arg2=[1.14, 5.79, 0.67, -984], arg3={"number": 1}
    ) == (708481, -722)

    with pytest.raises(CustomException):
        #  error message: we hate 1
        one_condition_custom_exception_and_return_binary_op_and_key(
            arg1="1", arg2=[1.14, 5.79, 0.67, 2.05], arg3={"number": 1}
        )
    one_condition_custom_exception_and_return_binary_op_and_key(
        arg1=166, arg2=[1.14, 5.79, 0.67, 935], arg3={"number": 1}
    )
    captured = capsys.readouterr()
    assert captured.out == "935 more when 2\n"



Introducing
-----------

Hi!

If you was hope to see information of production-ready solution - sorry, no.

This is just a try to create POC of idea to generate unit tests based on AST.

In source code you can see a mess with very strange constractions and a lot of 'TODO's
this is only because pack in very active development phase and I forget idea to plan it first and then develop,
because all my 'plans' crashed after adding support of 4-5 AST nodes and their combinations

You can think about this project like a something 'study':
I invistigate metaprogramming and AST in idea generate unittests from source code :)

And you can join me in this investigation if you interesting in this too!
So if you want to know how far this idea can go - join me in this interesting and fun road (check section Contributing)


Little bit of history
------------------

This is a 3rd version of package implementation, before using a mix of work with AST and tokenisation (current state)
I tried different ways:

1. inspect and other tools with live objects
2. only syntax and tokens + regexes

and the current state with AST.

I also checked packages that already exist, but they produce different result (but maybe you will be interesting
more in them, when in this project in-work, so I attach links, if you don't know yet this packages - check them):



Installation:
*************

    pip install laziest


Usage:
*************

    lazy /path/to/python/code/files


For example:

    lazy /home/yourUser/laziest/tests/code_sample/done/conditions.py


It will generate test file in directory:

    /home/yourUser/laziest/tests/test_conditions.py


Run tests with 'pytest' to check that they are valid:

    pytest /home/yourUser/laziest/tests/functional/test_primitive_code.py


Flag -d
*******

If you want to generate empty tests in case if code not supported by generator yet, you can use flag '-d'.
Output will be - generated modules for all functions, but without asserts, in body of function you will see a
comment with error and 'pass'.

For example, you have a code with logic, that not supported yet by generator, for example:

def string_format_named_three_args(arg1, arg2, arg3):
    return '{first} this is {name} ! {last}'.format(name=arg1, first=arg2, last=arg3)


If you run lazy with flag '-d' - you will have success test generation and in test module you will see for this function test:

def test_string_format_named_three_args():

    # string indices must be integers

    # Traceback (most recent call last):
    #  File "/Users/jvolkova/laziest/laziest/functions.py", line 163, in test_creation
    #    func_definition, func_name, func_data, class_, class_method_type)
    # TypeError: string indices must be integers
    #
    pass

Tests
*****

You can run laziest tests with tox and check output.



Contributing
************

Pull requests are welcome.

What and how you can contribute?

1. Ideas, comment to logic, some architecture and solutions plans - this is very welcome, because I works alone in
this thing and I can be very subjective and make wrong solutions.

2. Cases in laziest/tests/code_sample/todo.

How create case:


A. Use like a sample:
laziest/tests/code_sample/done/primitive_code.py

B. You need to add operations from simplest (if they was not covered in different cases) to most complicated.
So, if you want add into code cases this function:

def function_with_vars_operations(new_name, use_data, validate_len=True):
    if validate_len and len(new_name) > 15:
            raise Exception("Impossible to set so long name. Lenght of the name must be < 15 symbols)
    user_data['name'] = new_name
    return user_data

C. You must to be sure, that already supported (or covered by cases):

1. Functions with arguments
2. if statements
3. if statements with 2 or more conditions, because here we see 'validate_len' - first condition
    and 'len(new_name) > 15' - second condition
4. you need check that conditions like 'if something' are supported and covered or create cases for that separate.
Why does it matter? Because, 'if validate_len' under the hood mean 'validate_len != 0, validate_len != [],
    validate_len != () or any other empty container'
5. correct work with default values for 'validate_len=True' - so need 2 assert, test with default value and without
5. and etc.

D. Try to split your result on blocks, if you don't see in code samples something that already ready.
You also can just run generator on separated functions to see does generator cover test case correct or not.

For current example 'separated' functions can be at least (because 1 and 2 already supported):
1.

def function_with_multiple_if_conditions(new_name, use_data, validate_len):
    if validate_len != 0 and len(new_name) > 15:
            raise Exception("Impossible to set so long name. Lenght of the name must be < 15 symbols)
    return user_data


2. now same but with default value

def function_with_default_value(new_name, use_data, validate_len=True):
    if validate_len != False:
            raise Exception("Impossible to set so long name. Lenght of the name must be < 15 symbols)
    return user_data


3. now same but without '!='

def function_with_if_exist(new_name, use_data, validate_len=True):
    if validate_len:
            raise Exception("Impossible to set so long name. Lenght of the name must be < 15 symbols)
    return user_data

You can change places of 2 and 3 - this is not matter.

4. and at the end

def function_with_vars_operations(new_name, use_data, validate_len=True):
    if validate_len and len(new_name) > 15:
            raise Exception("Impossible to set so long name. Lenght of the name must be < 15 symbols)
    user_data['name'] = new_name
    return user_data

3. If you added some features in code, please make sure to update tests as appropriate:

    This is mean you add in laziest/tests/code_sample/done construction that successful covered by generator
and tests that was generated also passed.


License
*******

This project is licensed under the Apache License - see the `LICENSE`_ file for details

.. _`LICENSE`: LICENSE
