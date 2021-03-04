from typing import List
from snakemake.io import glob_wildcards, expand

def source_basenames(source_folder: str) -> List[str]:
    basenames = glob_wildcards(source_folder + "/{basename}.xml").basename
    return basenames


def target_filenames(target_folder: str, source_names: str) -> List[str]:
    filenames = expand(target_folder + '/{basename}.txt', basename=source_names)
    return filenames
