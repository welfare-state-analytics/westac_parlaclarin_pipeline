## parla_clarin_to_text     : extract text from Para-Clarin XML
"""
Transforms Para-Clarin XML file to TXT file
"""

transform_config = config['transformed_speeches']


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
    shell:
        """
        mkdir -p {params.target_folder}
        parla_transform {input.filename} --template-name {params.template} --output-filename {output.filename}
        """
