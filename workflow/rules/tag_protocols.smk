# type: ignore
# pylint: skip-file, disable-all, syntax-error

"""
PoS tags Parla-CLARIN XML files using Stanza.
"""
from os import makedirs
from os.path import join as jj

from pyriksprot import ITagger, SwedishDehyphenatorService, dedent, parlaclarin, tag_protocol_xml
from workflow.config import Config
from workflow.taggers import StanzaTagger, TaggerRegistry
from workflow.utility import check_cuda

typed_config: Config = typed_config

check_cuda()

def tagger(cfg: Config, disable_gpu: bool) -> ITagger:
    """Get tagger from registry."""
    return TaggerRegistry.get(
        tagger_cls=StanzaTagger,
        model=cfg.stanza_dir,
        dehyphen_opts=dict(
            word_frequency_filename=cfg.word_frequency.fullname,
            **cfg.dehyphen.opts
        ),
        use_gpu=not disable_gpu,
    )


ANNOTATION_FOLDER = typed_config.annotated_folder
makedirs(ANNOTATION_FOLDER, exist_ok=True)


# pylint: disable=syntax-error
rule tag_protocols:
    message:
        "step: tag_protocols"
    params:
        template=typed_config.extract_speeches.template,
    # threads: workflow.cores * 0.75
    input:
        filename=jj(typed_config.parla_clarin.folder, "{year}", "{basename}.xml"),
    output:
        filename=jj(ANNOTATION_FOLDER, "{year}", "{basename}.zip"),
    # message: "Tagging {input.filename}."
    run:
        try:
            # FIXME: Add options (storage_format, segment_skip_size, force) to config file:
            tag_protocol_xml(
                input.filename,
                output.filename,
                tagger(typed_config, disable_gpu=config.get("disable_gpu", 0) == 0),
                storage_format="json",
            )
        except Exception as ex:
            print(f"failed: parla_annotate {input.filename} --output-filename {output.filename}")
            raise
