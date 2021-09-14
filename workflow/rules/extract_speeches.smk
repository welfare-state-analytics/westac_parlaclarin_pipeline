# type: ignore
# pylint: skip-file, disable-all
"""
Transforms Para-Clarin XML file to TXT file
"""
import os
from os.path import join as jj

from pyriksprot import convert_protocol, path_add_suffix
from snakemake.io import ancient, expand, glob_wildcards
from workflow.config import Config

rule extract_speeches:
    message:
        "step: extract_speeches"
    # log:
    #     typed_config.log_path,
    params:
        template=typed_config.extract_speeches.template,
    input:
        filename=jj(typed_config.parla_clarin.folder, "{year}", "{basename}.xml"),
    output:
        filename=jj(typed_config.annotated_folder, "{year}", f"{{basename}}.{typed_config.target_extension}"),
    run:
        try:
            convert_protocol(input.filename, output.filename, params.template)
        except Exception as ex:
            print(
                f"failed: parla_transform {input.filename} --output-filename {output.filename} --template-name {params.template}"
            )
            raise
