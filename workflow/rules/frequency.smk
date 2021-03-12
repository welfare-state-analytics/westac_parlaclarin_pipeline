# pylint: skip-file, disable-all, E, W
## parla_clarin_to_text     : extract text from Para-Clarin XML
"""
Computes word frequency list
"""
from workflow.model import compute_word_frequencies
import os
import glob

word_frequency = config['word_frequency']

source_pattern = os.path.join(config['parla_clarin']["folder"], '*.xml')
output_filename = os.path.join(word_frequency['work_data_folder'], word_frequency['filename'])


rule word_frequency:
    message:
        "step: word_frequency"
    input:
        filenames=glob.glob(source_pattern),
    output:
        filename=output_filename,
    run:
        compute_word_frequencies(input.filenames, output.filename)
