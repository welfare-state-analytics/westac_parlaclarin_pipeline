"""Retrive config value(s) stored in specified config and print value(s) to stdout.

This module is used in Makefile(s) that uses run-time settings.

Example:

    $ python scripts/config_value.py --config-name=config.yml config.work_folders.data_folder

    /path/to/data

"""

import glob
from os import makedirs, remove
from os.path import isfile
from os.path import join as jj

import click
from loguru import logger
from pyriksprot import tag_protocol_xml
from pyriksprot.utility import strip_path_and_extension
from pyriksprot.workflows.tag import ITagger
from tqdm import tqdm

from workflow.config import Config
from workflow.config.typed_config import load_typed_config
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

    logger.info("loading tagger...")

    typed_config: Config = load_typed_config(config_filename)

    makedirs(target_folder, exist_ok=True)

    tagger: ITagger = TaggerRegistry.stanza(typed_config, disable_gpu=disable_gpu)
    logger.info("done!")

    check_cuda()

    source_files: list[str] = glob.glob(jj(source_folder, "*.xml"))
    print(source_files)


    for source_file in tqdm(source_files):

        target_file = jj(target_folder, f"{strip_path_and_extension(source_file)}.zip")

        if isfile(target_file):
            if not force:
                logger.info(f"skipping: {target_file} since it already exists")
                continue
            else:
                remove(target_file)

        logger.info(f"tagging: {source_file}")

        tag_protocol_xml(source_file, target_file, tagger, storage_format="json")

        logger.info(f"done: {source_file}")

    logger.info("Done!")


if __name__ == "__main__":
    main()


# ANNOTATION_FOLDER = typed_config.annotated_folder
# makedirs(ANNOTATION_FOLDER, exist_ok=True)

# def tagger():
#     return TaggerRegistry.stanza(typed_config, disable_gpu=disable_gpu)

# rule tag_protocols:
#     message:
#         "step: tag_protocols"
#     params:
#         template=typed_config.extract_speeches.template,
#     # threads: workflow.cores * 0.75
#     input:
#         filename=jj(typed_config.parla_clarin.folder, "{year}", "{basename}.xml"),
#     output:
#         filename=jj(ANNOTATION_FOLDER, "{year}", "{basename}.zip"),
#     # message: "Tagging {input.filename}."
#     run:
#         try:
#             tag_protocol_xml(
#                 input.filename,
#                 output.filename,
#                 tagger(),
#                 storage_format="json",
#             )
#         except Exception as ex:
#             print(f"failed: tag_protocols {input.filename} --output-filename {output.filename}")
#             raise
