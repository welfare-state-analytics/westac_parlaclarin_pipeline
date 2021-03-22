# type: ignore
# pylint: skip-file, disable-all
"""
Annotates ParlaCLARIN XML files and stores result in ZIP
"""
import os

from workflow.annotate.stanza import annotate_protocol, StanzaAnnotator
from workflow.config import Config
from sparv.core import paths

config: Config = config

stanza_models_folder: str = os.path.join(paths.data_dir, "models/stanza")

annotator = StanzaAnnotator(model_root=stanza_models_folder)


def get_annotator():
    global annotator
    return annotator or (annotator := StanzaAnnotator(model_root=stanza_models_folder))


ANNOTATION_FOLDER = config.annotated_folder
os.makedirs(ANNOTATION_FOLDER, exist_ok=True)


rule annotate_speeches:
    message:
        "step: annotate_speeches"
    params:
        template=config.extract_speeches.template,
    input:
        # ancient(config.word_frequency.file_path),
        filename=os.path.join(SOURCE_FOLDER, '{year}/{basename}.xml'),
    output:
        filename=os.path.join(ANNOTATION_FOLDER, '{year}/{basename}.zip'),
    run:
        try:
            annotate_protocol(input.filename, output.filename, get_annotator())
        except Exception as ex:
            print(f"failed: parla_annotate {input.filename} --output-filename {output.filename}")
            raise
