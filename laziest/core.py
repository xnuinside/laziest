import tabnanny
import subprocess

from ast import parse

from laziest.analyzer import Analyzer
from laziest.strings import test_method_prefix
from laziest.generator import generate_test_file_content
from laziest.conf.config import init_config, default_settings
from laziest.walker import PathWalker, FilteredPaths


tabnanny.verbose = True


def run_laziest(args):
    """ main method with call steps to run laziest """
    print(args)
    config_args = {arg: args[arg] for arg in args if arg in default_settings and args[arg] is not None}
    # init config
    cfg = init_config(config_args)
    print(config_args)
    path = args['path']
    print(cfg.recursive)
    fp = FilteredPaths(cfg.use_ignore_files)
    pw = PathWalker(path, fp, cfg.recursive)
    for python_file in pw.python_files:
        print(f'Run test generation for {python_file}')
        # run TestSetCreator to get list of expected test files
        append = False
        if not config_args['overwrite']:
            append = True
            # run differ, to collect existed file names and methods
            pass
        # validate '.py' file - check intends
        tabnanny.check(python_file)

        # run analyzer
        with open(python_file, "r") as source:
            tree = parse(source.read())
        an = Analyzer()
        an.visit(tree)
        an.report()

        # to get diff with existed tests
        signatures_list = {'classes': [], 'def': []}
        for class_ in an.tree['classes']:
            signatures_list['classes'].append(test_method_prefix + class_['name'])

        # run comparator to get list of tests that we need to add (add only tests that not exist in test file)

        # run test file generator
        tf_content = generate_test_file_content(an)

        if append:
            # append new tests to tf
            # if new method in test case for class - insert
            pass
        # save result to file

        # run autopep8 on test files
        # subprocess.Popen(args="autopep8 "
        # "--in-place --aggressive --aggressive .".split())