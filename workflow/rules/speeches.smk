## parla_clarin_to_text     : extract text from Para-Clarin XML
"""
Transforms Para-Clarin XML file to TXT file
"""
import os
from workflow.model import convert_protocol
transform_config = config['transformed_speeches']

os.makedirs(transform_config['folder'], exist_ok=True)


rule parla_clarin_to_speeches:
    message:
        "step: parla_clarin_to_speeches"
    params:
        template=transform_config['template'],
        target_folder=transform_config['folder'],
    input:
        filename=jj(config['parla_clarin']['folder'], '{basename}.xml'),
    output:
        filename=jj(transform_config["folder"], '{basename}.' + transform_config["extension"]),
    run:
        convert_protocol(input.filename, output.filename, params.template)

    # shell:
    #     """
    #     parla_transform {input.filename} --template-name {params.template} --output-filename {output.filename}
    #     """
