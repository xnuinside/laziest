""" command line for laziest unit test's skeleton generator """

import os
import sys
import logging
import argparse
from importlib import  util as imp_util

from laziest.parser import GeneratorTestsFiles

logger = logging.getLogger("laziest")

def check_path_action():
    class checkPathAction(argparse.Action):
        def __call__(self, parser, args, value, option_string=None):
            if type(value) is list:
                value = value[0]
            user_value = value
            if option_string == 'None':
                if not os.path.isdir(value):
                    _current_user = os.path.expanduser("~")
                    if not value.startswith(_current_user) \
                            and not value.startswith(os.getcwd()):
                        if os.path.isdir(os.path.join(_current_user, value)):
                            value = os.path.join(_current_user, value)
                        elif os.path.isdir(os.path.join(os.getcwd(), value)):
                            value = os.path.join(os.getcwd(), value)
                        else:
                            value = None
                    else:
                        value = None
            elif option_string == '--template-name':
                if not os.path.isdir(value):
                    if not os.path.isdir(os.path.join(args.target, value)):
                        value = None
            if not value:
                logger.error("Could not to find path %s. Please provide "
                             "correct path to %s option",
                             user_value, option_string)
                sys.exit(1)
            setattr(args, self.dest, value)
    return checkPathAction


def show_version():
    logger.info("Laziest version: %s", "0.0.1")


def create_tests_subparser(_subparsers):
    test_subparser = _subparsers.add_parser('tests')
    test_subparser.add_argument('python_file', help='Target *.py file base '
                                                    'for test generation',
                                nargs=1,
                                action=check_path_action())

    test_subparser.add_argument('-o', '--objects',
                                help='List of objects names what must be tested '
                                     '(functions, classes). Leave empty if you '
                                     'want generate tests for all objects '
                                     'in python_file', required=True,
                                nargs=1, action=check_path_action())
    test_subparser.add_argument('-s', '--save_to',
                                help="Path where ti generate "
                                     "test_*.py file.Usually "
                                     "in directory tests/",
                                default="tests/", required=False)

def create_new_subparser(_subparsers):

    new_subparser = _subparsers.add_parser('new',
                                           description="Create new "
                                                       "package with layout")

    new_subparser.add_argument('package_name',
                               help='Package name to create. It will be name'
                                    'of main project directory and name for'
                                    'all configs (setup.cfg, tox.ini and etc)',
                               nargs=1, action=check_path_action())

    new_subparser.add_argument('path', help='Path where will be created new'
                                            'package. If path tree does not '
                                            'exist, it will be created.'
                                            'Default: current work directory',
                               nargs='*', action=check_path_action(),
                               default="")
    new_subparser.add_argument('--project',
                               help='Name for Project and project directory, '
                                    'if not exist - used package_name')

    new_subparser.add_argument('-pd', '--package-dir',
                               help="Directory to store inside project dir")

    new_subparser.add_argument('--no-tox', help="To avoid creating tox.ini",
                               default=False, action="store_true")

def create_parser():
    parser = argparse.ArgumentParser(prog='laziest',
                                     description="Generator of test_*.py "
                                                 "files for your src")
    subparsers = parser.add_subparsers()
    create_tests_subparser(subparsers)
    parser.add_argument('-v', '--version', help="show laziest version",
                                action=show_version())

    return parser

def main():
    parser = create_parser()
    args = parser.parse_args()
    if args.tests:
        spec = imp_util.spec_from_file_location(
            "test_object", args.python_file)
        target_module = imp_util.module_from_spec(spec)
        spec.loader.exec_module(target_module)
        obj = eval("target_module.{}".format(args.objects))
        file_name = os.path.basename(args.python_file)
        path = args.save_to
        GeneratorTestsFiles(obj, file_name, path).generate_file()
    if args.new:
        pass

if __name__ == "__main__":
	main()

