# type: ignore
# pylint: skip-file, disable-all
"""
Computes global word frequency
"""
from workflow.model import compute_term_frequencies


rule word_frequency:
    message:
        "step: word_frequency"
    # log: LOG_NAME
    input:
        filenames=SOURCE_FILES,
    output:
        filename=config.word_frequency.file_path,
    run:
        compute_term_frequencies(input.filenames, output.filename)
