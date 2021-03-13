# type: ignore

import importlib.resources as pkg_resources
import logging
from importlib import import_module
from io import StringIO
from typing import Any, Union

import yaml

from .persistent_dict import PersistentDict
from .utils import (
    data_path_ts,
    dict_get_by_path,
    dotdict,
    download_url,
    flatten,
    hasattr_path,
    load_dict,
    load_token_set,
    lookup,
    path_add_date,
    path_add_sequence,
    path_add_suffix,
    path_add_timestamp,
    source_basenames,
    store_dict,
    store_token_set,
    strip_extensions,
    strip_path_and_add_counter,
    strip_path_and_extension,
    strip_paths,
    sync_delta_names,
    target_filenames,
    temporary_file,
    ts_data_path,
)
from .yaml_loader import ordered_dump, ordered_load

# # usage:
# ordered_dump(data, Dumper=yaml.SafeDumper)
# ordered_load(stream, yaml.SafeLoader)


def loads_yaml_config(m: Any, config_name: str) -> str:
    m = import_module(m) if isinstance(m, str) else m
    config_str = pkg_resources.read_text(m, config_name)
    return config_str


def load_yaml_config(m: Any, config_name: str) -> dict:
    config_str = loads_yaml_config(m, config_name)
    config = ordered_load(StringIO(config_str), Loader=yaml.SafeLoader)
    return config


def setup_logger() -> logging.Logger:

    log_format = '%(asctime)s, %(name)s, %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s'

    logging.basicConfig(
        format=log_format, datefmt=log_format, level=logging.INFO, filename='parla_clarin_pipeline.log', filemode='w'
    )

    formatter = logging.Formatter(log_format)

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    console.setLevel(logging.INFO)

    logger = logging.getLogger("parla_clarin_pipeline")
    logger.addHandler(console)
    logger.setLevel(logging.WARNING)

    return logger


logger: logging.Logger = setup_logger()
