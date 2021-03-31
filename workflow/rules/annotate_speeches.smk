# type: ignore
# pylint: skip-file, disable-all
"""
Annotates Parla-CLARIN XML files using Stanza.
"""
from os.path import join as jj
from os import makedirs

from workflow.annotate.stanza import StanzaAnnotator, annotate_protocol
from workflow.config import Config

config: Config = config
annotator: StanzaAnnotator = None


def get_annotator():
    global annotator
    if annotator is None:
        annotator = StanzaAnnotator(model_root=config.stanza_dir)
    return annotator


ANNOTATION_FOLDER = config.annotated_folder
makedirs(ANNOTATION_FOLDER, exist_ok=True)


rule annotate_speeches:
    message:
        "step: annotate_speeches"
    params:
        template=config.extract_speeches.template,
    input:
        # ancient(config.word_frequency.file_path),
        filename=jj(SOURCE_FOLDER, "{year}", "{basename}.xml"),
    output:
        filename=jj(ANNOTATION_FOLDER, "{year}", "{basename}.zip"),
    run:
        try:
            annotate_protocol(input.filename, output.filename, get_annotator())
        except Exception as ex:
            print(f"failed: parla_annotate {input.filename} --output-filename {output.filename}")
            raise
