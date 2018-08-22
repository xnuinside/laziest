Laziest
=======

Unittests plot generator for Python

Tested with Python3.6


Simple example
==============

We have file class_for_test.py with class inside class::

    ClassForTest(object):

        def __init__(self):
            pass

        def method(self):
            pass

        def method_second(self):
            pass

        def new_method(self):
            pass


We start command::

    laziest class_for_test.py -o ClassForTest

After command in directory "./tests" will be created file with name "test_class_for_test.py" with content::

    import unittest

    class TestClassForTest(unittest.TestCase):

        def test_method(self):
            pass

        def test_method_second(self):
            pass

        def test_new_method(self):
            pass


    if __name__ == "__main__":
        unittest.main()

What are the skeleton - plot for unittests

