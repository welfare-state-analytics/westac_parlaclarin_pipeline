from typing import Union
import click
import workflow.config as config_module
from workflow.config import load_yaml_config, SafeLoaderIgnoreUnknown
from workflow.model.utility import dict_get_by_path
import json

@click.command()
@click.argument('config_keys', nargs=-1)
@click.option(
    '-t',
    '--config-name',
    default='config.yml',
    help='Config name',
)
def main(
    config_keys: str = None,
    config_name: str = None,
) -> None:

    config: dict = load_yaml_config(config_module, config_name, SafeLoaderIgnoreUnknown)

    for config_key in config_keys:
        value: Union[dict, str] = dict_get_by_path(config, config_key)

        if isinstance(value, dict):
            value = json.dumps(value)
        elif value is None:
            value = ""

        click.echo(value)


if __name__ == "__main__":
    main()

