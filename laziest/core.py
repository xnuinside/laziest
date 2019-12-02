import tabnanny
import subprocess
from ast import parse
from typing import Text
from laziest.analyzer import Analyzer
from laziest.strings import test_method_prefix
from laziest.generator import generate_test_file_content
from laziest.conf.config import init_config, default_settings
from laziest.walker import PathWalker, FilteredPaths
import os

tabnanny.verbose = True

def dump_to_file(path: Text, tf_content: Text) -> Text:
    test_file_name = f'test_{os.path.basename(path)}'
    test_file_path = os.path.join(os.path.dirname(path), test_file_name)
    with open(test_file_path, 'w+') as test_file:
        test_file.write(tf_content)
    return test_file_path


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
        if not config_args.get('overwrite', False):
            append = True
            # run differ, to collect existed file names and methods
            pass
        # validate '.py' file - check intends
        tabnanny.check(python_file)

        # run analyzer
        with open(python_file, "r") as source:
            source_massive = source.read()
            tree = parse(source_massive)
        an = Analyzer(source_massive)
        an.visit(tree)
        an.report()

        # to get diff with existed tests
        signatures_list = {'classes': [], 'def': []}
        for class_ in an.tree['classes']:
            signatures_list['classes'].append(test_method_prefix + class_['name'])

        # run comparator to get list of tests that we need to add (add only tests that not exist in test file)

        # run test file generator
        tf_content = generate_test_file_content(an, path)
        print(tf_content)
        if append:
            # append new tests to tf
            # if new method in test case for class - insert
            pass
        test_file_paht = dump_to_file(path, tf_content)
        subprocess.Popen(f'black -l {79} {test_file_paht}', shell=True)

# path  to your file to test
path = ''
arg = {'path': path}
run_laziest(args=arg)