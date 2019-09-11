## Laziest

Laziest is a tool that generate unittests blueprint for Python code using pytest

To use:

    laziest  path_to_python_file 
    or
    laziest . # to run tests in current dir

### Python versions Support:

Tested with Python3.7


###  Simple example for Unittests generation

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

    laziest tests class_for_test.py -o ClassForTest

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

### Arguments and options

For example: 

    laziest new ./target_dir project-name -r --no-tox --project new_project --source-dir src --no-docs --req lala,test

All possible cli args described in:

    src/laziest/conf/cli.yaml
   

### Priority of defined params

1 - Higher, 3 - Lower

1. Console args
2. Configs: laziest.cfg -> tox.ini -> setup.cfg -> default params from laziest/conf/default_conf.cfg
3. Params typers can be found in laziest/conf/default_conf.cfg after ':' notation


### Laziest Diagram: How it works

https://drive.google.com/file/d/1x6wX-uyOi5A2ffoK6N5eXkUUu3fF3VWT/view?usp=sharing


### TODO

1. Normal documentation for methods 

### Maintenance






