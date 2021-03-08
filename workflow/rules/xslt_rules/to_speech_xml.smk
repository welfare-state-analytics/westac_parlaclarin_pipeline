import sys

sys.path.insert(0, '/home/roger/source/welfare-state-analytics/penelope_parla_clarin_pipeline')

from pipelines.snakeline.rules import utility

## parla_clarin_to_text     : extract text from Para-Clarin XML
"""
Transforms Para-Clarin XML to a simplified Speech XML format where the entire speech is merged into one block.
"""


rule parla_clarin_to_u_csv:
    message:
        "Step: parla_clarin_to_text"
    params:
        xslt=config['parla_clarin_extract_xslt'],
    input:
        xml_file=jj(config['parla_clarin']['folder'], '{basename}.xml'),
    output:
        txt_file=jj(config["target_export_folder"], 'parla_clarin_text', '{basename}.txt'),
    shell:
        """
        snakemake -jar lib/saxon-he.jar {input.xml_file} {params.xslt} > {output.txt_file}
        """


rule parla_clarin_sync_text:
    run:
        utility.sync_delta_names(
            config['parla_clarin']['folder'], "xml", config['target_export_folder'], "txt", delete=True
        )