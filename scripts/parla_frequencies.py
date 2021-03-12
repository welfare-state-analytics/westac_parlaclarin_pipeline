import sys

import click
from workflow.model import compute_word_frequencies

@click.command()
@click.argument('input-folder', type=click.STRING)
@click.argument('output-filename', type=click.STRING)
def main(
    input_folder: str = None,
    output_filename: str = None,
):

    try:
        compute_word_frequencies(input_folder, output_filename)
    except Exception as ex:
        click.echo(ex)
        sys.exit(1)


if __name__ == "__main__":
    main()
