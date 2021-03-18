# type: ignore
# pylint: skip-file, disable-all
"""
Transforms Para-Clarin XML file to TXT file
"""
import os
from workflow.model import convert_protocol
from snakemake.io import expand, glob_wildcards, ancient
from workflow.model.utility import path_add_suffix
from workflow.config import Config

config: Config = config

rule extract_speeches:
    message:
        "step: extract_speeches"
    # log:
    #     path_add_suffix(LOG_NAME, "{year}_{basename}"),
    params:
        template=config.extract_speeches.template,
    input:
        ancient(config.word_frequency.file_path),
        filename=os.path.join(SOURCE_FOLDER, '{year}/{basename}.xml')
    output:
        filename=os.path.join(TARGET_FOLDER, f'{{year}}/{{basename}}.{TARGET_EXTENSION}'),
    run:
        try:
            convert_protocol(input.filename, output.filename, params.template)
        except Exception as ex:
            print(f"failed: parla_transform {input.filename} --output-filename {output.filename} --template-name {params.template}")
            raise
