# type: ignore
# pylint: skip-file, disable-all
"""
Transforms Para-Clarin XML file to TXT file
"""
import os
from workflow.model import convert_protocol
from snakemake.io import expand, glob_wildcards
from workflow.model.utility import path_add_suffix


rule extract_speeches:
    message:
        "step: extract_speeches"
    # log:
    #     path_add_suffix(LOG_NAME, "{year}_{basename}"),
    params:
        template=config.extract_speeches.template,
    input:
        filename=jj(SOURCE_FOLDER, '{year}/{basename}.xml'),
    output:
        filename=jj(TARGET_FOLDER, f'{{year}}/{{basename}}.{TARGET_EXTENSION}'),
    run:
        convert_protocol(input.filename, output.filename, params.template)
