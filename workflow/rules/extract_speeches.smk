# type: ignore
# pylint: skip-file, disable-all
"""
Transforms Para-Clarin XML file to TXT file
"""
import os
from workflow.model import convert_protocol
from snakemake.io import expand, glob_wildcards
from workflow.model.utility import path_add_suffix

year_folders = expand(f'{TARGET_FOLDER}/{{year}}', year=glob_wildcards(os.path.join(SOURCE_FOLDER, f"{{year}}")))


rule dirs:
    # log: path_add_suffix(LOG_NAME, "{year}")
    input:
        jj(SOURCE_FOLDER, "{year}"),
    output:
        folder=directory(jj(TARGET_FOLDER, "{year}")),
    run:
        os.makedirs(output.folder, exist_ok=True)


rule extract_speeches:
    message:
        "step: extract_speeches"
    log:
        path_add_suffix(LOG_NAME, "{year}_{basename}"),
    params:
        template=config.extract_speeches.template,
    input:
        filename=jj(SOURCE_FOLDER, '{year}/{basename}.xml'),
        folders=year_folders,
    output:
        filename=jj(TARGET_FOLDER, '{year}/{basename}' + TARGET_EXTENSION),
    run:
        convert_protocol(input.filename, output.filename, params.template)
