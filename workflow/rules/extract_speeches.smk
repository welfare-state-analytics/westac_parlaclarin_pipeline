# type: ignore
# pylint: skip-file, disable-all
"""
Transforms Para-Clarin XML file to TXT file
"""
import os
from workflow.model import convert_protocol
from snakemake.io import expand, glob_wildcards


year_folders = expand(
    f'{TARGET_FOLDER}/{{year}}',
    year=glob_wildcards(os.path.join(SOURCE_FOLDER, f"{{year}}"))
)

rule dirs:
    input: jj(SOURCE_FOLDER, f"{{year}}")
    output: jj(f'{TARGET_FOLDER}/{{year}}')
    run: os.makedirs(f'{TARGET_FOLDER}/{{year}}', exists_ok=True)


rule extract_speeches:
    message:
        "step: extract_speeches"
    params:
        template = config.extract_speeches.template,
    input:
        filename = jj(SOURCE_FOLDER, '{year}/{basename}.xml'),
        folders = year_folders
    output:
        filename = jj(TARGET_FOLDER, f'{{year}}/{{basename}}.{TARGET_EXTENSION}'),
    run:
        convert_protocol(input.filename, output.filename, params.template)
