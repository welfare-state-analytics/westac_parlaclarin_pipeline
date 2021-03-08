## parla_clarin_to_text     : extract text from Para-Clarin XML
"""
Transforms Para-Clarin XML to a simplified Speech XML format where the entire speech is merged into one block.
"""


rule parla_clarin_xml_to_xml:
    message:
        "Step: parla_clarin_xml_to_xml"
    params:
        xslt=config['speeches.template'],
    input:
        xml_file=jj(config['parla_clarin']['folder'], '{basename}.xml'),
    output:
        txt_file=jj(config["target_export_folder"], 'parla_clarin_text', '{basename}.txt'),
    shell:
        """
        snakemake -jar lib/saxon-he.jar {input.xml_file} {params.xslt} > {output.txt_file}
        """
