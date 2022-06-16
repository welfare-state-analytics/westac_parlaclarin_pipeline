import click
from loguru import logger
from pyriksprot.workflows.tag import ITagger, tag_protocols

from workflow.config import Config
from workflow.taggers import TaggerRegistry
from workflow.utility import check_cuda


@click.command()
@click.argument('source_folder')
@click.argument('target_folder')
@click.argument('config_filename')
@click.option('--force', is_flag=True, default=False, help='Force if exists')
@click.option('--disable-gpu', is_flag=True, default=False, help='Disable GPU')
def main(
    source_folder: str = None,
    target_folder: str = None,
    config_filename: str = None,
    force: bool = False,
    disable_gpu: bool = False,
) -> None:

    check_cuda()
    config: Config = Config.load(config_filename)

    tagger: ITagger = TaggerRegistry.stanza(config, disable_gpu=disable_gpu)

    tag_protocols(tagger=tagger, source_folder=source_folder, target_folder=target_folder, force=force)

    logger.info("workflow ended")


if __name__ == "__main__":
    main()
