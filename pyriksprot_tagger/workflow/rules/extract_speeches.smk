# type: ignore
# pylint: skip-file, disable-all
"""
Transforms Para-Clarin XML file to TXT file
"""
from os.path import join as jj

from pyriksprot.parlaclarin.convert import convert_protocol

rule extract_speeches:
    message:
        "step: extract_speeches"
    # log:
    #     typed_config.get("log_filename"),
    params:
        template=typed_config.get("extract.template"),
    input:
        filename=jj(typed_config.get("corpus.folder"), "{year}", "{basename}.xml"),
    output:
        filename=jj(typed_config.get("tagged_frames.folder"), "{year}", f"{{basename}}.{typed_config.get('target.extension')}"),
    run:
        try:
            convert_protocol(input.filename, output.filename, params.template)
        except Exception as ex:
            print(
                f"failed: parla_transform {input.filename} --output-filename {output.filename} --template-name {params.template}"
            )
            raise
