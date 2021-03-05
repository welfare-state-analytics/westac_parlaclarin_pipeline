from __future__ import annotations

import os
import time
from typing import TYPE_CHECKING, List, TypeVar, Union
import typing

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


def strip_path_and_extension(filename: str) -> List[str]:
    return os.path.splitext(os.path.basename(filename))[0]


def strip_extensions(filename: Union[str, List[str]]) -> List[str]:
    if isinstance(filename, str):
        return os.path.splitext(filename)[0]
    return [os.path.splitext(x)[0] for x in filename]


def path_add_suffix(path: str, suffix: str, new_extension: str = None) -> str:
    basename, extension = os.path.splitext(path)
    return f'{basename}{suffix}{extension if new_extension is None else new_extension}'


def path_add_timestamp(path: str, fmt: str = "%Y%m%d%H%M") -> str:
    return path_add_suffix(path, f'_{time.strftime(fmt)}')


def path_add_date(path: str, fmt: str = "%Y%m%d") -> str:
    return path_add_suffix(path, f'_{time.strftime(fmt)}')


def ts_data_path(directory: str, filename: str):
    return os.path.join(directory, f'{time.strftime("%Y%m%d%H%M")}_{filename}')


def data_path_ts(directory: str, path: str):
    name, extension = os.path.splitext(path)
    return os.path.join(directory, '{}_{}{}'.format(name, time.strftime("%Y%m%d%H%M"), extension))


def path_add_sequence(path: str, i: int, j: int = 0) -> str:
    return path_add_suffix(path, f"_{str(i).zfill(j)}")


def strip_path_and_add_counter(filename: str, i: int, n_zfill: int = 3):
    return f'{os.path.basename(strip_extensions(filename))}_{str(i).zfill(n_zfill)}.txt'


def strip_paths(filenames: Union[str, List[str]]) -> Union[str, List[str]]:
    if isinstance(filenames, str):
        return os.path.basename(filenames)
    return [os.path.basename(filename) for filename in filenames]

T = TypeVar("T")

def flatten(lofl: List[List[T]]) -> List[T]:
    """Returns a flat single list out of supplied list of lists."""

    return [item for sublist in lofl for item in sublist]
