""" command line for laziest unit test's skeleton generator """

import os
import logging
from importlib import util as imp_util

from laziest.parser import GeneratorTestsFiles
from laziest.blueprint import PackageCreator
from clifier import clifier

logger = logging.getLogger("laziest")


def main():
    config_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "conf/cli.yaml")
    cli = clifier.Clifier(config_path, prog_version="0.0.1")
    parser = cli.create_parser()
    args = parser.parse_args()
    if 'python_file' in args:
        spec = imp_util.spec_from_file_location(
            "test_object", args.python_file)
        target_module = imp_util.module_from_spec(spec)
        spec.loader.exec_module(target_module)
        obj = eval("target_module.{}".format(args.objects))
        file_name = os.path.basename(args.python_file)
        path = args.save_to
        GeneratorTestsFiles(obj, file_name, path).generate_file()
    if 'package_name' in args:
        PackageCreator(args).create_structure()


if __name__ == "__main__":
    main()
