""" module contains logic to create diff with existed tests """
import os
from typing import Text, Union
from pathlib import Path
from laziest.conf.config import logger

INIT_FILE = '__init__.py'


def get_main_folder(path: Text) -> Path:
    """ get main folder, where must be placed test dir """
    path = os.path.dirname(os.fspath(path)) \
        if os.path.isfile(path) else os.fspath(path)
    n = 2

    while n >= 0:
        n -= 1
        path_content = os.listdir(path)
        if INIT_FILE not in path_content or n < 0:
            return path
        else:
            path = os.path.dirname(path)


def resolve_test_path(tests_path: Path, main_folder: Text) -> Path:
    """
        prepare a directory for unittests or check what already exist
    :param tests_path:
    :param main_folder:
    :return:
    """
    if tests_path.exists():
        if tests_path.is_file():
            raise ValueError("Test path {} is file! Please remove file "
                             "or set another path".format(tests_path))
    else:
        tests_path = Path(os.path.join(main_folder, os.fspath(tests_path)))

        logger.info("Test path does ot exist {}. Creating test folder".format(
            os.path.abspath(tests_path)))
        os.makedirs(tests_path, exist_ok=True)
    check_and_create_init_file(tests_path)

    return tests_path


def create_empty_file(path: Union[Path, str]) -> None:
    with open(path, "w+") as test_init:
        test_init.writelines([""])


def check_and_create_init_file(dir_path: Path) -> None:
    init_file = dir_path.joinpath(INIT_FILE)

    if not init_file.exists():
        logger.info("__init__.py in test dir does not exist. "
                    "Creating empty file: {}".format(init_file))
        create_empty_file(init_file)
