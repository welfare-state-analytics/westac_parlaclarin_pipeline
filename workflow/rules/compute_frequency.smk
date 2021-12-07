# type: ignore
# pylint: skip-file, disable-all
"""
Computes global word frequency
"""
from pyriksprot import compute_term_frequencies

# TODO: Apply optional wildcard constraint (if any)
WORD_FREQUENCY_SOURCE_FILES = glob.glob(jj(typed_config.parla_clarin.folder, "*", "*.xml"))

rule word_frequency:
    message:
        "step: word_frequency"
    input:
        filenames=WORD_FREQUENCY_SOURCE_FILES,
    output:
        filename=typed_config.word_frequency.fullname,
    run:
        compute_term_frequencies(
            source=input.filenames,
            filename=output.filename,
            segment_skip_size=10,
            multiproc_processes=config.get('processes', 1),
            multiproc_keep_order=False,
        )
