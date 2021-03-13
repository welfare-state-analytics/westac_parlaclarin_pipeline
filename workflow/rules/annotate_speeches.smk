# type: ignore
# pylint: skip-file, disable-all
"""
Annotates Speeches XML files to TXT file
"""
import os
from workflow.model import convert_protocol
from workflow.model.utility import dotdict

transform_config = dotdict(config['transformed_speeches'])
os.makedirs(transform_config['folder'], exist_ok=True)


rule annotate_speeches:
    message:
        "step: annotate_speeches"
    params:
        template = transform_config.template,
        target_folder = transform_config.folder,
    input:
        filename = jj(config.parla_clarin.folder, '{basename}.xml'),
    output:
        filename = jj(transform_config.folder, '{basename}.' + transform_config.extension),
    run:
        convert_protocol(input.filename, output.filename, params.template)
