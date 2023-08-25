import click
from loguru import logger
from pyriksprot import configuration
from pyriksprot.workflows.tag import ITagger, TaggerProvider, tag_protocols
from pyriksprot_tagger.utility import check_cuda


@click.command()
@click.argument('config_filename')
@click.argument('source_folder')
@click.argument('target_folder')
@click.option('--force', is_flag=True, default=False, help='Force if exists')
@click.option('--recursive', is_flag=True, default=True, help='Recurse subfolders')
@click.option('--pattern', type=str, default="**/prot-*.xml", help='Recurse subfolders')
def main(
    config_filename: str,
    source_folder: str,
    target_folder: str,
    force: bool = False,
    recursive: bool = True,
    pattern: str = "**/prot-*.xml",
) -> None:
    tagit(
        config_filename=config_filename,
        source_folder=source_folder,
        target_folder=target_folder,
        force=force,
        recursive=recursive,
        pattern=pattern,
    )


def tagit(
    config_filename: str,
    source_folder: str,
    target_folder: str,
    force: bool = False,
    recursive: bool = True,
    pattern: str = "**/prot-*.xml",
):
    check_cuda()

    configuration.configure_context(source=config_filename, context="default")

    tagger: ITagger = TaggerProvider.tagger_factory().create()

    tag_protocols(
        tagger=tagger,
        source_folder=source_folder,
        target_folder=target_folder,
        force=force,
        recursive=recursive,
        pattern=pattern,
    )

    logger.info("workflow ended")


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
    # tagit("sample-data/config.yml", "sample-data/v0.6.0/parlaclarin/protocols/", "sample-data/v0.6.0/tagged_frames")
