from __future__ import annotations

import contextlib
import errno
import os
import sys
from os.path import isdir
from os.path import join as jj
from typing import Any

from pyriksprot import (  # pylint: disable=unused-import
    deprecated,
    ensure_path,
    flatten,
    hasattr_path,
    lookup,
    norm_join,
    path_add_date,
    path_add_sequence,
    path_add_suffix,
    path_add_timestamp,
    strip_extensions,
    strip_path_and_extension,
    strip_paths,
    sync_delta_names,
    temporary_file,
    touch,
    ts_data_path,
    unlink,
)
from snakemake.io import expand, glob_wildcards
from snakemake.logging import logger, setup_logger

# try:
#     from sparv.core import paths  # type: ignore
#     SPARV_DATADIR: str = paths.data_dir
# except ImportError:
#     logger.warning("Sparv is not avaliable")
#     SPARV_DATADIR = os.environ.get('SPARV_DATADIR')
#     if SPARV_DATADIR is None:
#         logger.error("SPARV_DATADIR is not set!")

SPARV_DATADIR = os.environ.get('SPARV_DATADIR')
STANZA_DATADIR = os.environ.get('STANZA_DATADIR')


def expand_basenames(source_folder: str, source_extension: str, years: int = None):
    opts_digits: str = r'\d*'
    any_digits: str = r'\d+'
    year_constraint: str = (
        rf"{{year,{years}\d*}}"
        if isinstance(
            years,
            (int, str),
        )
        else f"{{year,{'|'.join(f'{y}{opts_digits}' for y in years)}}}"
        if isinstance(years, list)
        else rf"{{year,{any_digits}}}"
    )
    source_years, target_basenames = glob_wildcards(jj(source_folder, year_constraint, f"{{file}}.{source_extension}"))
    return source_years, target_basenames


def expand_target_files(
    source_folder: str, source_extension: str, target_folder: str, target_extension: str, years: int = None
) -> list[str]:

    source_years, target_basenames = expand_basenames(source_folder, source_extension, years=years)

    target_files = expand(
        jj(target_folder, "{year}", f"{{basename}}.{target_extension}"),
        zip,
        year=source_years,
        basename=target_basenames,
    )

    return target_files


def setup_logging():

    with contextlib.suppress(Exception):

        if sys.platform == "win32":

            def handler(msg):
                if isinstance(msg, str):
                    print(msg)
                if isinstance(msg, dict):
                    if 'level' in msg and 'debug' in msg['level']:
                        return
                    if 'msg' in msg:
                        print(f"{msg.get('level', '')}: {msg['msg']}")
                        return
                print(msg)

            logger.log_handler = []

            setup_logger(handler=[handler])


WINDOWS_ERROR_INVALID_NAME = 123


def is_valid_path(pathname: str) -> bool:
    """Check if `pathname`is a valid path
    Source: https://stackoverflow.com/questions/9532499/
    """
    try:
        if not isinstance(pathname, str) or not pathname:
            return False
        _, pathname = os.path.splitdrive(pathname)
        root_dir = _root_folder()
        for part in pathname.split(os.path.sep):
            try:
                os.lstat(root_dir + part)
            except OSError as exc:
                if hasattr(exc, 'winerror'):
                    if exc.winerror == WINDOWS_ERROR_INVALID_NAME:  # pylint: disable=no-member
                        return False
                elif exc.errno in {errno.ENAMETOOLONG, errno.ERANGE}:
                    return False
    except TypeError:
        return False
    return True


def _root_folder():
    if sys.platform != 'win32':
        return os.path.sep
    return os.environ.get('HOMEDRIVE', 'C:').rstrip(os.path.sep) + os.path.sep


def check_cuda() -> None:
    with contextlib.suppress(Exception):
        import torch  # pylint: disable=import-outside-toplevel

        print(f"CUDA is{' ' if torch.cuda.is_available() else ' NOT '}avaliable!")
        if not torch.cuda.is_available():
            print(
                "Please try (windows): pip install torch==1.7.0 torchvision==0.8.1 -f https://download.pytorch.org/whl/cu101/torch_stable.html"
            )


def sparv_datadir(root_folder: str):

    if SPARV_DATADIR is not None:
        return SPARV_DATADIR

    for folder in ["..", "."]:
        sparv_folder = jj(root_folder, folder, "sparv")
        if isdir(sparv_folder):
            return sparv_folder

    return None


def stanza_dir(root_folder: str) -> str:
    _sparv_datadir = sparv_datadir(root_folder)
    _stanza_dir: str = (
        STANZA_DATADIR
        if STANZA_DATADIR is not None
        else jj(_sparv_datadir, "models", "stanza")
        if _sparv_datadir is not None
        else None
    )

    if _stanza_dir is None:
        logger.error("Stanza data dir not found: STANZA_DATADIR, SPARV_DATADIR not set")
        return None

    if not isdir(_stanza_dir):
        raise FileNotFoundError(f"Stanza models folder {_stanza_dir}")

    return _stanza_dir


def dotget(data: dict, path: str | list[str], default: Any = None) -> Any:

    if path is None or not data:
        return default

    ps: list[str] = path if isinstance(path, (list, tuple)) else [path]

    d = None

    for p in ps:
        d = data
        for attr in p.split('.'):

            d: dict = d.get(attr) if isinstance(d, dict) else None

            if d is None:
                break

        if d is not None:
            return d

    return d or default


def dget(data: dict, *paths: list[str], default: Any = None) -> Any:

    return dotget(data, paths, default)
