""" command line for laziest unit test's skeleton generator """

import os
import sys
import argparse
import logging
from importlib import util as imp_util

from laziest.parser import GeneratorTestsFiles
from clifier import clifier

logger = logging.getLogger("laziest")

def check_path_action():
    class CheckPathAction(argparse.Action):
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
    return CheckPathAction


def show_version():
    logger.info("Laziest version: %s", "0.0.1")


def main():
    config_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "conf/cli.yaml")
    cli = clifier.Clifier(config_path)
    cli.add_actions((show_version, check_path_action))
    parser = cli.create_parser()
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

