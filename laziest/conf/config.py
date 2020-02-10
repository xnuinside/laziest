"""
    supported config files in order how conf searches
        start from left to right
    console -> laziest.cfg -> tox.ini -> setup.cfg -> if nothing, use default settings

    laziest.cfg must be placed in current work directory from that you start command or from cli arg -c --config
        same for tox.ini and setup.cfg config files

    to define laziest settings in all config files must be defined section [laziest], example:

        setup.cfg some content...
        ....

        [laziest]
        test_path = unit_tests/
        ignore_file_names = "without_tests.py"
        use_ignore_file = .dockerignore, .gitignore

    Config params:

    1. *use_ignore_file*
    Give possibility to add to tests all paths that already defined in list of ignore files,
    you can create your separate path ignore file, only one criteria - it must contain list of valid paths,
    one per line similar to '.dockerignore' or '.gitignore' files

    Example:
        use_ignore_file = .dockerignore, .gitignore
"""
import os
import logging
from configparser import ConfigParser
from collections import OrderedDict
from typing import Dict, Union
from copy import deepcopy

logger = logging.getLogger('laziest')

section_name = 'laziest'
default_config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'default_conf.cfg')

config = None


def load_config(path: str) -> ConfigParser:
    cfg = ConfigParser()
    cfg.read(path)
    return cfg


# load config with default params
default_config = load_config(default_config_path)[section_name]

# list with params types
params_types = {key: eval(default_config[key].split(':')[1]) for key in default_config.keys()}
print(params_types)
# get default settings
default_settings = {key: eval(f"{default_config[key].split(':')[1]}(\'{default_config[key].split(':')[0]}\')")
                    for key in default_config.keys()}

print(default_settings)
config_paths = OrderedDict({
    'laziest.cfg': '.',
    'tox.ini': '.',
    'setup.cfg': '.'
})


class Config:
    """ Config file - singleton class store configuration for laziest, one per run """

    __slots__ = [key for key in default_settings]

    __instance = None

    def __new__(cls, *args):
        if Config.__instance is None:
            Config.__instance = object.__new__(cls)
        return Config.__instance

    def __init__(self, params):
        for param in params:
            try:
                self.__setattr__(param, self.get_valid_type(param, params[param]))
            except AttributeError:
                logger.error(f'Impossible to set {param} as parameter for Laziest.\n'
                             f'Possible options: {", ".join(list(default_settings.keys()))}.'
                             f'Please, remove wrong parameter to continue.')
                exit(1)

    def update(self, values_dict: Dict):
        for param in values_dict:
            self.__setattr__(param, self.get_valid_type(param, values_dict[param]))

    @staticmethod
    def get_valid_type(key, value):
        if value:
            print(key, value)
            if isinstance(value, str) and ',' in value:
                value = value.split(',')
            if params_types[key] == 'list' and not isinstance(value, list):
                value = [value]
            else:
                if not isinstance(value, params_types[key]):
                    print(params_types)
                    print(key)
                    print(value)
                    value = params_types[key](value)
        return value


def get_config(args: Dict) -> Config:
    """
        get laziest configuration based on args from cli and default/from config settings
    :param args: args from cli
    :return:
    """
    params_not_in_args = [arg for arg in default_settings.keys() if arg not in args]
    if params_not_in_args:
        # if not all params come from cli - load default and settings from config
        return read_config_from_file(args)
    return Config(args)


def read_config_from_file(args):
    """
        args that comes from cli (we overwrite all config settings with args from cli)
    :param args: dict key - value with laziest params
    :return: dict with params from config
    """
    from_config_file = find_config()
    if from_config_file:
        from_config_file.update(args)
    return from_config_file


def get_config_based_on_config_file(path: str) -> Union[Config, None]:
    """
        load config and check if section exist or not
    :param path: path to config file
    :return: None if section [laziest] not exist in Config object updated with params from section if exist
    """
    cfg = load_config(path)
    if section_name not in cfg.sections():
        return None
    else:
        cfg = config[section_name]
        common_params = deepcopy(default_settings)
        params_from_config = {key: cfg[key] for key in cfg.keys()}
        common_params.update(params_from_config)
        return Config(common_params)


def find_config() -> Union[Config, None]:
    """
        try to fins [laziest] sections in 3 configs:
            laziest.cfg -> tox.ini -> setup.cfg
        if found -> stop iterate on configs, merge found settings with default (overwrite default)
    :return: Config object with params loaded from file and merged with default settings
    """
    for config_name in config_paths:
        path_to_config = os.path.join(config_paths[config_name], config_name)
        if os.path.exists(path_to_config):
            cfg = get_config_based_on_config_file(path_to_config)
            if cfg:
                break
    else:
        cfg = Config(default_settings)
    return cfg


def init_config(args: Dict) -> Config:
    """ init Conig singleton and write to global variable, one instance per run"""
    global config

    config = get_config(args)
    return config
