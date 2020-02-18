Laziest
=======

Generator of test_*.py files for your Python code.
Package that trying generate unit tests for you.


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

I also check packages that already exist, but they produce different result (but maybe you will be interesting
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


You can run laziest tests with tox and check output.


Docs:
*****

Coming soon.

Contributing
************

Pull requests are welcome.

What and how you can contribute?

1. Ideas, comment to logic, some architecture and solutions plans - this is very welcome, because I works alone in
this thing and I can be very subjective and make wrong solutions.

2. Cases in laziest/tests/code_sample/todo.

How create case:

    1. Use lake sample:
    laziest/tests/code_sample/done/primitive_code.py

    2. You need to add operations from simplest (if they was not covered in different cases) to most complicated.
    So, if you want add into code cases this function:

    def function_with_vars_operations(new_name, use_data, validate_len=True):
        if validate_len and len(new_name) > 15:
                raise Exception("Impossible to set so long name. Lenght of the name must be < 15 symbols)
        user_data['name'] = new_name
        return user_data

    You must to be sure, that already supported (or covered by cases):

    1. Functions with arguments
    2. if statements
    3. if statements with 2 or more conditions, because here we see 'validate_len' - first condition
        and 'len(new_name) > 15' - second condition
    4. you need check that conditions like 'if something' are supported and covered or create cases for that separate.
    Why does it matter? Because, 'if validate_len' under the hood mean 'validate_len != 0, validate_len != [],
        validate_len != () or any other empty container'
    5. correct work with default values for 'validate_len=True' - so need 2 assert, test with default value and without
    5. and etc.

    So, try to split your result on blocks, if you don't see in code samples something that already ready.
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



For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate:

    This is mean you add in laziest/tests/code_sample/done function/class/another language
construction that successful covered by generator and tests, that was generated also passed.






License
*******

This project is licensed under the Apache License - see the `LICENSE`_ file for details

.. _`LICENSE`: LICENSE
