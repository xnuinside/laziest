import os
from clifier import clifier
from laziest.core import run_laziest


def init_cli():
    # init cli from config
    config_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "cli.yaml")
    cli = clifier.Clifier(config_path, prog_version="0.0.3")
    parser = cli.create_parser()
    # get args from cli
    args = parser.parse_args().__dict__
    # run laziest
    run_laziest(args)


if __name__ == "__main__":
    init_cli()
