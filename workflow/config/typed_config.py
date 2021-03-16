import importlib.resources as pkg_resources
import os
from collections import OrderedDict
from dataclasses import dataclass
from importlib import import_module
from io import StringIO
from typing import Any, Type

import yaml

from .. import config as config_module


def ordered_load(stream, Loader=yaml.SafeLoader, object_pairs_hook=OrderedDict):
    class OrderedLoader(Loader):  # pylint: disable=too-many-ancestors
        pass

    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))

    OrderedLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_mapping)
    return yaml.load(stream, OrderedLoader)


def ordered_dump(data, stream=None, Dumper: Type[yaml.SafeDumper] = yaml.SafeDumper, **kwds):
    class OrderedDumper(Dumper):  # pylint: disable=too-many-ancestors
        pass

    def _dict_representer(dumper: yaml.SafeDumper, data):
        return dumper.represent_mapping(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, data.items())

    OrderedDumper.add_representer(OrderedDict, _dict_representer)
    return yaml.dump(data, stream, OrderedDumper, **kwds)


def loads_yaml_config(m: Any, config_name: str) -> str:
    m = import_module(m) if isinstance(m, str) else m
    config_str = pkg_resources.read_text(m, config_name)
    return config_str


def load_yaml_config(m: Any, config_name: str) -> dict:
    config_str = loads_yaml_config(m, config_name)
    config = ordered_load(StringIO(config_str), Loader=yaml.SafeLoader)
    return config


class WorkFoldersConfig(yaml.YAMLObject):
    yaml_tag = "!work_folders"

    def __init__(self) -> None:
        self.data_folder: str

    def __repr__(self):
        return f"{self.__class__.__name__}(data_folder={self.data_folder})"

    @property
    def log_folder(self):
        return os.path.join(self.data_folder, 'logs')


class ParlaClarinConfig(yaml.YAMLObject):
    yaml_tag: str = u'!parla_clarin'

    def __init__(self):
        self.repository_folder: str
        self.repository_url: str
        self.folder: str

    def __repr__(self):
        return f"{self.__class__.__name__}(repository_folder={self.repository_folder},repository_url={self.repository_url},folder={self.folder})"

    @property
    def source_pattern(self):
        return os.path.join(self.folder, '*.xml')

    @property
    def repository_parent_folder(self):
        return os.path.abspath(os.path.join(self.repository_folder, '..'))


class TransformedSpeechesConfig(yaml.YAMLObject):
    yaml_tag: str = u'!extract_speeches'

    def __init__(self):
        self.folder: str
        self.template: str
        self.extension: str

    def __repr__(self):
        return f"{self.__class__.__name__}(folder={self.folder},template={self.template},extension={self.extension})"


class WordFrequencyConfig(yaml.YAMLObject):
    yaml_tag: str = u'!word_frequency'

    def __init__(self):
        self.data_folder: str
        self.filename: str

    def __repr__(self):
        return f"{self.__class__.__name__}(data_folder={self.data_folder},filename={self.filename})"

    @property
    def file_path(self):
        return os.path.join(self.data_folder, self.filename)


class DehyphenConfig(yaml.YAMLObject):
    yaml_tag: str = u'!dehyphen'

    def __init__(self):
        self.data_folder: str
        self.whitelist_filename: str
        self.whitelist_log_filename: str
        self.unresolved_filename: str

    def __repr__(self):
        return (
            f"{self.__class__.__name__}"
            f"(data_folder={self.data_folder},"
            f"whitelist_filename={self.whitelist_filename},"
            f"whitelist_log_filename={self.whitelist_log_filename},"
            f"unresolved_filename={self.unresolved_filename})"
        )

    @property
    def whitelist_path(self):
        return os.path.join(self.data_folder, self.whitelist_filename)

    @property
    def whitelist_log_path(self):
        return os.path.join(self.data_folder, self.whitelist_log_filename)

    @property
    def unresolved_path(self):
        return os.path.join(self.data_folder, self.unresolved_filename)


@dataclass
class Config(yaml.YAMLObject):

    yaml_tag: str = u'!config'

    work_folders: WorkFoldersConfig = None
    parla_clarin: ParlaClarinConfig = None
    extract_speeches: TransformedSpeechesConfig = None
    word_frequency: WordFrequencyConfig = None
    dehyphen: DehyphenConfig = None

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(work_folders={self.work_folders},"
            f"parla_clarin={self.parla_clarin},"
            f"extract_speeches={self.extract_speeches},"
            f"word_frequency={self.word_frequency},"
            f"dehyphen={self.dehyphen})"
        )

    @property
    def data_folder(self) -> str:
        return self.work_folders.data_folder

    @data_folder.setter
    def data_folder(self, value: str):
        self.work_folders.data_folder = value
        self.word_frequency.data_folder = value
        self.dehyphen.data_folder = value


def loads_typed_config(config_str: str) -> Config:
    data = yaml.full_load(StringIO(config_str))
    cfg = data.get('config')
    return cfg


def load_typed_config(config_name: str) -> Config:
    # FIXME: Error checks
    yaml_str = loads_yaml_config(config_module, config_name)
    cfg = loads_typed_config(yaml_str)
    return cfg
