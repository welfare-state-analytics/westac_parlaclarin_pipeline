import glob
import sys

import click
from workflow.model import Protocol, ProtocolConverter
from workflow.model.utility import strip_paths
from resources.templates import PARLA_TEMPLATES_SHORTNAMES


@click.command()
@click.argument('input_filename', type=click.STRING)
@click.option(
    '-o',
    '--output-filename',
    default=None,
    help='Output filename (default stdout)',
    type=click.STRING,
)
@click.option(
    '-t',
    '--template-name',
    default='speeches.xml',
    type=click.Choice(PARLA_TEMPLATES_SHORTNAMES),
    help='Template to use',
)
@click.option('-b', '--flag/--no-flag', default=True, is_flag=True, help='Use word baseforms')
def main(
    input_filename: str = None,
    output_filename: str = None,
    template_name: str = None,
    flag: bool = True,
):

    try:

        protocol: Protocol = Protocol.from_file(input_filename)

        converter: ProtocolConverter = ProtocolConverter(template_name)

        content: str = converter.convert(protocol, strip_paths(input_filename))

        if output_filename is not None:
            with open(output_filename, "w") as fp:
                fp.write(content)
        else:
            click.echo(content, nl=False)

    except Exception as ex:
        click.echo(ex)
        sys.exit(1)


if __name__ == "__main__":
    main()
