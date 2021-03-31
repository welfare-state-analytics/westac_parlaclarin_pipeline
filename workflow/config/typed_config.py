import importlib.resources as pkg_resources
import os
from collections import OrderedDict
from dataclasses import dataclass
from importlib import import_module
from io import StringIO
from typing import Any, Type

import yaml

from .. import config as config_module
from ..model.utility import norm_join as nj


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


class SafeLoaderIgnoreUnknown(yaml.SafeLoader):  # pylint: disable=too-many-ancestors
    def let_unknown_through(self, _, node):
        return self.construct_mapping(node)


SafeLoaderIgnoreUnknown.add_multi_constructor('!', SafeLoaderIgnoreUnknown.let_unknown_through)


def loads_yaml_config(m: Any, config_name: str) -> str:
    m = import_module(m) if isinstance(m, str) else m
    config_str = pkg_resources.read_text(m, config_name)
    return config_str


def load_yaml_config(m: Any, config_name: str, loader=yaml.SafeLoader) -> dict:
    config_str = loads_yaml_config(m, config_name)
    config = ordered_load(StringIO(config_str), Loader=loader)
    return config


class WorkFoldersConfig(yaml.YAMLObject):
    yaml_tag = "!work_folders"

    def __init__(self, data_folder: str) -> None:
        self.data_folder: str = nj(data_folder)

    def __repr__(self):
        return f"{self.__class__.__name__}(data_folder={self.data_folder})"

    def normalize(self) -> "WorkFoldersConfig":
        self.data_folder = nj(self.data_folder)
        return self

    @property
    def log_folder(self) -> str:
        return nj(self.data_folder, 'logs')


class ParlaClarinConfig(yaml.YAMLObject):
    yaml_tag: str = u'!parla_clarin'

    def __init__(self, repository_folder: str, folder: str, repository_url: str):
        self.repository_folder: str = repository_folder
        self.folder: str = folder
        self.repository_url: str = repository_url

    def __repr__(self):
        return f"{self.__class__.__name__}(repository_folder={self.repository_folder},repository_url={self.repository_url},folder={self.folder})"

    @property
    def source_pattern(self) -> str:
        return nj(self.folder, '*.xml')

    def normalize(self) -> "ParlaClarinConfig":
        self.repository_folder = nj(self.repository_folder)
        self.folder = nj(self.folder)
        return self

    @property
    def repository_parent_folder(self):
        return os.path.abspath(nj(self.repository_folder, '..'))


class TransformedSpeechesConfig(yaml.YAMLObject):
    yaml_tag: str = u'!extract_speeches'

    def __init__(self, folder: str, template: str, extension: str):
        self.folder: str = folder
        self.template: str = template
        self.extension: str = extension

    def __repr__(self):
        return f"{self.__class__.__name__}(folder={self.folder},template={self.template},extension={self.extension})"

    def normalize(self) -> "TransformedSpeechesConfig":
        self.folder = nj(self.folder)
        return self


class WordFrequencyConfig(yaml.YAMLObject):
    yaml_tag: str = u'!word_frequency'

    def __init__(self, data_folder: str, filename: str):
        self.data_folder: str = data_folder
        self.filename: str = filename

    def __repr__(self):
        return f"{self.__class__.__name__}(data_folder={self.data_folder},filename={self.filename})"

    def normalize(self) -> "WordFrequencyConfig":
        self.data_folder = nj(self.data_folder)
        return self

    @property
    def file_path(self) -> str:
        return nj(self.data_folder, self.filename)


class DehyphenConfig(yaml.YAMLObject):
    yaml_tag: str = u'!dehyphen'

    def __init__(
        self, data_folder: str, whitelist_filename: str, whitelist_log_filename: str, unresolved_filename: str
    ):
        self.data_folder: str = data_folder
        self.whitelist_filename: str = whitelist_filename
        self.whitelist_log_filename: str = whitelist_log_filename
        self.unresolved_filename: str = unresolved_filename

    def normalize(self) -> "DehyphenConfig":
        self.data_folder = nj(self.data_folder)
        return self

    def __repr__(self):
        return (
            f"{self.__class__.__name__}"
            f"(data_folder={self.data_folder},"
            f"whitelist_filename={self.whitelist_filename},"
            f"whitelist_log_filename={self.whitelist_log_filename},"
            f"unresolved_filename={self.unresolved_filename})"
        )

    @property
    def whitelist_path(self) -> str:
        return nj(self.data_folder, self.whitelist_filename)

    @property
    def whitelist_log_path(self) -> str:
        return nj(self.data_folder, self.whitelist_log_filename)

    @property
    def unresolved_path(self) -> str:
        return nj(self.data_folder, self.unresolved_filename)


@dataclass
class Config(yaml.YAMLObject):

    yaml_tag: str = u'!config'

    work_folders: WorkFoldersConfig = None
    parla_clarin: ParlaClarinConfig = None
    extract_speeches: TransformedSpeechesConfig = None
    word_frequency: WordFrequencyConfig = None
    dehyphen: DehyphenConfig = None
    annotated_folder: str = None

    def normalize(self) -> "DehyphenConfig":
        self.annotated_folder = nj(self.annotated_folder)
        self.work_folders.normalize()
        self.parla_clarin.normalize()
        self.extract_speeches.normalize()
        self.word_frequency.normalize()
        self.dehyphen.normalize()
        return self

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(work_folders={self.work_folders},"
            f"parla_clarin={self.parla_clarin},"
            f"extract_speeches={self.extract_speeches},"
            f"word_frequency={self.word_frequency},"
            f"dehyphen={self.dehyphen},"
            f"annotated_folder={self.annotated_folder})"
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
    cfg: Config = data.get('config')
    return cfg.normalize()


def load_typed_config(config_name: str) -> Config:
    yaml_str = loads_yaml_config(config_module, config_name)
    cfg = loads_typed_config(yaml_str)
    return cfg
