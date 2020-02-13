Laziest
=======
Generator of test_*.py files for your Python code


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

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

License
*******

This project is licensed under the Apache License - see the `LICENSE`_ file for details

.. _`LICENSE`: LICENSE
