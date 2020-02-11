import os
import tabnanny
import subprocess
from ast import parse
from typing import Text
import multiprocessing as mp
from laziest.analyzer import Analyzer
from laziest.strings import test_method_prefix
from laziest.generator import generate_test_file_content
from laziest.conf.config import init_config, default_settings
from laziest.walker import PathWalker, FilteredPaths


tabnanny.verbose = True

q = mp.Queue()


def dump_to_file(path: Text, tf_content: Text, tests_dir: Text) -> Text:
    test_file_name = f'test_{os.path.basename(path)}'
    test_file_path = os.path.join(tests_dir, test_file_name)
    with open(test_file_path, 'w+') as test_file:
        test_file.write(tf_content)
    return test_file_path


def run_laziest(args: dict):
    """ main method with call steps to run laziest """
    config_args = {arg: args[arg] for arg in args if arg in default_settings and args[arg] is not None}
    # init config
    cfg = init_config(config_args)
    path = args['path']
    if not os.path.exists(path):
        raise Exception(f'Path {path} not exists')
    fp = FilteredPaths(cfg.use_ignore_files)
    pw = PathWalker(path, fp, cfg.recursive)
    # get paths to python modules
    paths = [x for x in pw.python_files if '__init__' not in x]

    # if not config_args.get('overwrite', False):
    # append = True
    # run differ, to collect existed file names and methods
    # pass
    generate_bunch_of_test_files(paths)
    exit(0)


def generate_bunch_of_test_files(python_paths):
    num_cores = mp.cpu_count()
    pool = mp.Pool(num_cores)
    jobs = []

    for python_file in python_paths:
        jobs.append(pool.apply_async(tests_generator_per_file, (python_file,)))

    # wait for all jobs to finish
    for job in list(jobs):
        job.get()
    while not q.empty():
        proc = subprocess.Popen(f'black -l {79} {q.get()}', shell=True)
        proc.wait()
        proc.kill()

    pool.close()
    pool.join()


def tests_generator_per_file(python_file):
    print(f'Run test generation for {python_file}')
    # run TestSetCreator to get list of expected test files
    append = False
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

    # run test file generator
    tf_content = generate_test_file_content(an, python_file)
    if append:
        # append new tests to tf
        # if new method in test case for class - insert
        pass

    # TODO: need to change on getting prefix from command line and config
    prefix = 'tests'
    if prefix in python_file:
        tests_dir = os.path.join(python_file.split(prefix)[0], prefix)
    else:
        tests_dir = os.path.join(os.path.dirname(os.path.dirname(python_file)), 'tests')
    os.makedirs(tests_dir, exist_ok=True)
    test_file_path = dump_to_file(python_file, tf_content, tests_dir)
    q.put(test_file_path)
