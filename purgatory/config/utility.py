import os
from os.path import isdir, join

from loguru import logger

try:
    from sparv.core import paths  # type: ignore

    SPARV_DATADIR: str = paths.data_dir
except ImportError:
    logger.warning("Sparv is not avaliable")
    SPARV_DATADIR = os.environ.get('SPARV_DATADIR')
    if SPARV_DATADIR is None:
        logger.error("SPARV_DATADIR is not set!")

STANZA_DATADIR = os.environ.get('STANZA_DATADIR')


def sparv_datadir(root_folder: str):

    if SPARV_DATADIR is not None:
        return SPARV_DATADIR

    for folder in ["..", "."]:
        sparv_folder = join(root_folder, folder, "sparv")
        if isdir(sparv_folder):
            return sparv_folder

    return None


def stanza_dir(root_folder: str) -> str:
    _sparv_datadir = sparv_datadir(root_folder)
    _stanza_dir: str = (
        STANZA_DATADIR
        if STANZA_DATADIR is not None
        else join(_sparv_datadir, "models", "stanza")
        if _sparv_datadir is not None
        else None
    )

    if _stanza_dir is None:
        logger.error("Stanza data dir not found: STANZA_DATADIR, SPARV_DATADIR not set")
        return None

    if not isdir(_stanza_dir):
        raise FileNotFoundError(f"Stanza models folder {_stanza_dir}")

    return _stanza_dir
