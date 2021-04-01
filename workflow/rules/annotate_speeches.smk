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

try:
    import torch
    print(f"CUDA is{' ' if torch.cuda.is_available() else ' NOT '}avaliable!")
    if not torch.cuda.is_available():
        print("Please try (on windows): pip install torch==1.7.0 torchvision==0.8.1 -f https://download.pytorch.org/whl/cu101/torch_stable.html")
except:
    pass


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
