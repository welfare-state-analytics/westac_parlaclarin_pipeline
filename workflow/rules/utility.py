from __future__ import annotations
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Set

from snakemake.io import glob_wildcards


def sync_delta_names(source_folder: str, source_extension: str, target_folder: str, target_extension: str, delete: bool=False) -> Set(str):
    """Returns basenames in targat_folder that doesn't exist in source folder (with respectively extensions)
    """
    source_names = glob_wildcards(os.path.join(source_folder , "/{basename}" + source_extension)).basename
    target_names = glob_wildcards(os.path.join(target_folder , "/{basename}" + target_extension)).basename

    delta_names = set(target_names).difference(set(source_names))

    if delete:
        for basename in delta_names:
            os.unlink(os.path.join(target_folder , f"{basename}.{target_extension}"))

    return delta_names
