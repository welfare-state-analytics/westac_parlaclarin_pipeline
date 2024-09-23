# type: ignore
# pylint: skip-file, disable-all
"""
Computes global word frequency
"""
import glob
from pyriksprot import compute_term_frequencies

WORD_FREQUENCY_SOURCE_FILES = glob.glob(jj(typed_config.get("corpus.folder"), "*", typed_config.get("corpus.pattern")))

rule word_frequency:
    message:
        "step: word_frequency"
    input:
        filenames=WORD_FREQUENCY_SOURCE_FILES,
    output:
        filename=typed_config.get("dehyphen.tf_filename"),
    run:
        compute_term_frequencies(
            source=input.filenames,
            filename=output.filename,
            segment_skip_size=10,
            multiproc_processes=config.get('processes', 1),
            multiproc_keep_order=False,
        )
