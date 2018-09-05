## Laziest

Laziest is a tool kit for Python Developers that provide such features:

1. Creating Python Project layout (Blueprint) with files for correct packaging inside: setup.cfg, setup.py, tox.ini, requirements.txt, README.md, test dir, docs dir and etc.

To use: 

    laziest new target_folder package_name
 
2. Generating unittests blueprint for Python code

To use:

    laziest tests path_to_python_file -o class_name


### Python versions Support:

Tested with Python3.6


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
    
If you want to get full list of possible commands:

    use:
        laziest tests -h
    or:  
        laziest new -h
        
Or read file with all commands:

    src/laziest/conf/cli.yaml
   

Priority of defined params
==========================
1 - Higher, 3 - Lower

1. Console args
2. Config project
3. Default configs: .pip.conf, .pydistutils.cfg, .laziest.ini


