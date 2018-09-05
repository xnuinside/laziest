"""   default properties:
    - constants defined in defaults.py
    - read config folder from XDG_CONFIG_HOME
    - get from pip.conf section
    - get from .pydistutils section
"""

import os
import sys


INIT_FILE = "__init__.py"
TOX_FILE = "tox.ini"
SETUP_PY = "setup.py"
SETUP_CFG = "setup.cfg"
README_FILE = "README.md"
REQUIREMENTS_FILE = "requirements.txt"

pj_files = [TOX_FILE, SETUP_PY, SETUP_CFG, README_FILE]


TEST_DIR = 'tests/unittests'
DOC_DIR = "doc"
pj_dirs = [TEST_DIR, DOC_DIR]

# Files content

setup_py_content = """

from setuptools import setup

setup()

"""

setup_cfg_content = """
[metadata]

version = {version}
name = {package_name}
long_description = file:README.md
long_description_content_type=text/markdown
"""
init_py_content = ""

tox_ini_content = """
[tox]
envlist = flake8

[testenv:flake8]
deps = flake8

commands =
    flake8 ./{package_name}
    flake8 ./{test_dir}
"""

README_md_content = ""

requirements_txt_content = ""

home_dir = os.path.expanduser("~/")
config_folder = os.environ.get("XDG_CONFIG_HOME", None) or os.path.join(
    home_dir, "~/.config")


class Config(object):
    def __init__(self, args):
        pip_env_var = os.environ.get("PIP_CONFIG_FILE")

        if not pip_env_var:
            self.get_path_to_pip_conf()

    @staticmethod
    def get_path_to_pip_conf():
        """
        function to crete list of possible paths, depend on
        sys.platform and check which conf exist

        If multiple configuration files are found by pip then they are combined in the following order:

        The site-wide file is read
        The per-user file is read
        The virtualenv-specific file is read

        """

        if sys.platform == 'win':
            paths_to_pip_conf_per_user = [os.path.join(home_dir, '\pip\pip.ini')]
            _app_data_path = os.path.join(os.getenv('APPDATA'), None)
            if not _app_data_path:
                print("ERROR: Could not found APPDATA variable. "
                      "Need path to %APPDATA% folder")
            else:
                paths_to_pip_conf_per_user.append(
                    os.path.join(_app_data_path, "pip\pip.ini"))
        else:
            paths_to_pip_conf_per_user = [os.path.join(home_dir, '.pip/pip.conf'),
                                          os.path.join(
                                              config_folder, '/pip/pip.conf')]
            if sys.platform == 'darwin':
                paths_to_pip_conf_per_user.append(os.path.join(
                    home_dir, "Library/Application Support/pip/pip.conf"))
