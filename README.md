## Laziest

Status: POC in process, research

Readme: TODO

To play: 

fill 'path' arg in core.py with absolute path to file tests/unittests/primitive_code.py 
it must be like:

    # in core.py
    # path  to your file to test
    path = '/Users/your_user/laziest/tests/unittests/primitive_code.py'
    arg = {'path': path}
    run_laziest(args=arg)