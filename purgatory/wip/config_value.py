"""Retrive config value(s) stored in specified config and print value(s) to stdout.

This module is used in Makefile(s) that uses run-time settings.

Example:

    $ python scripts/config_value.py configs/config.yml config.data_folder

    /path/to/data

"""

import json
from typing import Union

import click
from workflow.config import Config


@click.command()
@click.argument('filename')
@click.argument('config_keys', nargs=-1)
def main(filename: str = None, config_keys: str = None) -> None:

    config: dict = Config.load(filename)
    values = []
    for config_key in config_keys:
        value: Union[dict, str] = dotget(config, config_key)

        if isinstance(value, dict):
            value = json.dumps(value)
        elif value is None:
            value = ""
        values.append(value)

    print(' '.join(values))


if __name__ == "__main__":
    main()
