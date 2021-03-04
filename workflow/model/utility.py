from __future__ import annotations

import os
from typing import TYPE_CHECKING, List

from snakemake.io import expand, glob_wildcards

if TYPE_CHECKING:
    from typing import Set


def source_basenames(source_folder: str) -> List[str]:
    basenames = glob_wildcards(source_folder + "/{basename}.xml").basename
    return basenames


def target_filenames(target_folder: str, source_names: str) -> List[str]:
    filenames = expand(target_folder + '/{basename}.txt', basename=source_names)
    return filenames


def sync_delta_names(
    source_folder: str, source_extension: str, target_folder: str, target_extension: str, delete: bool = False
) -> Set(str):
    """Returns basenames in targat_folder that doesn't exist in source folder (with respectively extensions)"""
    source_names = glob_wildcards(os.path.join(source_folder, "/{basename}" + source_extension)).basename
    target_names = glob_wildcards(os.path.join(target_folder, "/{basename}" + target_extension)).basename

    delta_names = set(target_names).difference(set(source_names))

    if delete:
        for basename in delta_names:
            os.unlink(os.path.join(target_folder, f"{basename}.{target_extension}"))

    return delta_names
