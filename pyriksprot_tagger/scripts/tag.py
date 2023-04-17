import click
from loguru import logger
from pyriksprot.workflows.tag import ITagger, tag_protocols
from pyriksprot_tagger import check_cuda
from pyriksprot_tagger.taggers import StanzaTaggerFactory


@click.command()
@click.argument('source_folder')
@click.argument('target_folder')
@click.argument('config_filename')
@click.option('--force', is_flag=True, default=False, help='Force if exists')
@click.option('--recursive', is_flag=True, default=True, help='Recurse subfolders')
@click.option('--disable-gpu', is_flag=True, default=False, help='Disable GPU')
def main(
    source_folder: str = None,
    target_folder: str = None,
    force: bool = False,
    recursive: bool = False,
    disable_gpu: bool = False,
) -> None:

    check_cuda()

    tagger: ITagger = StanzaTaggerFactory(use_gpu=not disable_gpu).create()

    tag_protocols(
        tagger=tagger, source_folder=source_folder, target_folder=target_folder, force=force, recursive=recursive
    )

    logger.info("workflow ended")


if __name__ == "__main__":
    main()
