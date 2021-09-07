# type: ignore
# pylint: skip-file, disable-all
"""
Annotates Parla-CLARIN XML files using Stanza.
"""
from os import makedirs
from os.path import join as jj

# from loguru import logger
from workflow.annotate import StanzaTagger, tag_protocol_xml
from workflow.config import Config
from workflow.model.convert import dedent, dehyphen, pretokenize
from workflow.model.dehyphenation.swe_dehyphen import SwedishDehyphenator, SwedishDehyphenatorService

typed_config: Config = typed_config

_tagger: StanzaTagger = None

try:
    import torch
    print(f"CUDA is{' ' if torch.cuda.is_available() else ' NOT '}avaliable!")
    if not torch.cuda.is_available():
        print("Please try (windows): pip install torch==1.7.0 torchvision==0.8.1 -f https://download.pytorch.org/whl/cu101/torch_stable.html")
except:
    pass

def get_tagger() -> StanzaTagger:
    global _tagger, typed_config, config
    if _tagger is None:
        use_gpu: bool = config.get("disable_gpu", 0) != 1
        preprocessors = [ dedent, dehyphen, str.strip, pretokenize ]
        _tagger = StanzaTagger(model_root=typed_config.stanza_dir, preprocessors=preprocessors, use_gpu=use_gpu)
    return _tagger


ANNOTATION_FOLDER = typed_config.annotated_folder
makedirs(ANNOTATION_FOLDER, exist_ok=True)


# pylint: disable=syntax-error
rule annotate_speeches:
    message:
        "step: annotate_speeches"
    params:
        template=typed_config.extract_speeches.template,
    # threads: workflow.cores * 0.75
    input:
        # ancient(typed_config.word_frequency.file_path),
        filename=jj(typed_config.parla_clarin.folder, "{year}", "{basename}.xml"),
    output:
        filename=jj(ANNOTATION_FOLDER, "{year}", "{basename}.zip"),
    # message: "Tagging {input.filename}."
    run:
        try:
            tag_protocol_xml(input.filename, output.filename, get_tagger())
        except Exception as ex:
            print(f"failed: parla_annotate {input.filename} --output-filename {output.filename}")
            raise
