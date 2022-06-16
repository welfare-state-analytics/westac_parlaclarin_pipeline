"""Retrive config value(s) stored in specified config and print value(s) to stdout.

This module is used in Makefile(s) that uses run-time settings.

Example:

    $ python scripts/config_value.py --config-name=config.yml config.data_folder

    /path/to/data

"""

import json
from typing import Union

import click
from workflow.config import Config
from workflow.utility import dict_get_by_path


@click.command()
@click.argument('config_keys', nargs=-1)
@click.option('-t', '--config-name', default='config.yml', help='Config filename')
def main(
    config_keys: str = None,
    filename: str = None,
) -> None:

    config: dict = Config.load(filename)
    values = []
    for config_key in config_keys:
        value: Union[dict, str] = dict_get_by_path(config, config_key)

        if isinstance(value, dict):
            value = json.dumps(value)
        elif value is None:
            value = ""
        values.append(value)

    print(' '.join(values))


if __name__ == "__main__":
    main()
