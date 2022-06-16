# type: ignore
# pylint: skip-file, disable-all, syntax-error

"""
PoS tags Parla-CLARIN XML files using Stanza.
"""
from os import makedirs
from os.path import join as jj

from pyriksprot import tag_protocol_xml

from workflow.config import Config
from workflow.taggers import TaggerRegistry
from workflow.utility import check_cuda

typed_config: Config = typed_config
disable_gpu: bool = config.get("disable_gpu", 0) == 1

check_cuda()

ANNOTATION_FOLDER = typed_config.tagged_frames_folder
makedirs(ANNOTATION_FOLDER, exist_ok=True)

def tagger():
    return TaggerRegistry.stanza(typed_config, disable_gpu=disable_gpu)

rule tag_protocols:
    message:
        "step: tag_protocols"
    params:
        template=typed_config.extract_opts.template,
    # threads: workflow.cores * 0.75
    input:
        filename=jj(typed_config.corpus.source_folder, "{year}", "{basename}.xml"),
    output:
        filename=jj(ANNOTATION_FOLDER, "{year}", "{basename}.zip"),
    # message: "Tagging {input.filename}."
    run:
        try:
            tag_protocol_xml(
                input.filename,
                output.filename,
                tagger(),
                storage_format="json",
            )
        except Exception as ex:
            print(f"failed: tag_protocols {input.filename} --output-filename {output.filename}")
            raise
