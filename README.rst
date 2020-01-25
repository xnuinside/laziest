Laziest
=======
Generator of test_*.py files for your Python code


Installation:
*************

    pip install laziest

Usage:
*************

    laziest /path/to/python/code/files

For example:

    laziest /home/youruser/laziest/tests/functional/primitive_code.py

It will generate test file in directory:

    /home/youruser/laziest/tests/functional/test_primitive_code.py

Run tests with 'pytest' to check that they are valid:

    pytest /home/youruser/laziest/tests/functional/test_primitive_code.py
