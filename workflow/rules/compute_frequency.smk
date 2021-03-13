# type: ignore
# pylint: skip-file, disable-all
"""
Computes word frequency list
"""
from workflow.model import compute_word_frequencies
from workflow.config.typed_config import WordFrequencyConfig
import os
import glob

word_frequency_config: WordFrequencyConfig = config.word_frequency

source_pattern = os.path.join(config.parla_clarin.folder, '*.xml')


rule word_frequency:
    message:
        "step: word_frequency"
    input:
        filenames = glob.glob(source_pattern),
    output:
        filename = word_frequency_config.file_path,
    run:
        compute_word_frequencies(input.filenames, output.filename)
