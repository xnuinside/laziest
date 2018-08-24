""" default properties:
    - constants defined in defaults.py
    - get from pip.conf section
    - get from .pydistutils section
"""

INIT_FILE = "__init__.py"
TOX_FILE = "tox.ini"
SETUP_PY = "setup.py"
SETUP_CFG = "setup.cfg"

project_files = [TOX_FILE, SETUP_PY, SETUP_CFG]

SETUP_PY_content = """

from setuptools import setup

setup()

"""

SETUP_CFG_content = """

[metadata]

"""
INIT_FILE_content = ""

TOX_FILE = """

[tox]
envlist = flake8

[testenv:flake8]
deps = flake8

commands =
    flake8 ./

"""
