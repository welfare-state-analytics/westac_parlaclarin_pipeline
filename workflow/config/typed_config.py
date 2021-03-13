from io import StringIO
from multiprocessing import parent_process
import os

import yaml

from .. import config as config_module
from ..model.utility import loads_yaml_config


class WorkFoldersConfig(yaml.YAMLObject):
    yaml_tag = "!work_folders"

    def __init__(self) -> None:
        self.data_folder: int

    def __repr__(self):
        return f"{self.__class__.__name__}(data_folder={self.data_folder})"


class ParlaClarinConfig(yaml.YAMLObject):
    yaml_tag: str = u'!parla_clarin'

    def __init__(self):
        self.repository_folder: str
        self.repository_url: str
        self.folder: str

    def __repr__(self):
        return f"{self.__class__.__name__}(repository_folder={self.repository_folder},repository_url={self.repository_url},folders={self.folders})"


class TransformedSpeechesConfig(yaml.YAMLObject):
    yaml_tag: str = u'!transformed_speeches'

    def __init__(self):
        self.folder: str
        self.template: str
        self.extension: str

    def __repr__(self):
        return f"{self.__class__.__name__}(folder={self.folder},template={self.template},extension={self.extension})"


class WordFrequencyConfig(yaml.YAMLObject):
    yaml_tag: str = u'!word_frequency'

    def __init__(self):
        self.work_folders: WorkFoldersConfig
        self.filename: str

    def __repr__(self):
        return f"{self.__class__.__name__}(filename={self.filename})"

    @property
    def file_path(self):
        return os.path.join(self.work_folders.data_folder, self.filename)

class DehyphenConfig(yaml.YAMLObject):
    yaml_tag: str = u'!dehyphen'

    def __init__(self):
        self.work_folders: WorkFoldersConfig
        self.whitelist_filename: str
        self.whitelist_log_filename: str
        self.unresolved_filename: str

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(whitelist_filename={self.whitelist_filename},"
            f"whitelist_log_filename={self.whitelist_log_filename},unresolved_filename={self.unresolved_filename})"
        )


class Config(yaml.YAMLObject):
    yaml_tag: str = u'!config'

    def __init__(self):
        self.work_folders: WorkFoldersConfig
        self.parla_clarin: ParlaClarinConfig
        self.transformed_speeches: TransformedSpeechesConfig
        self.word_frequency: WordFrequencyConfig
        self.dehyphen: DehyphenConfig

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(work_folders={self.work_folders},"
            f"parla_clarin={self.parla_clarin},"
            f"transformed_speeches={self.transformed_speeches},"
            f"word_frequency={self.word_frequency},"
            f"dehyphen={self.dehyphen})"
        )


def load_typed_config(config_name: str) -> Config:
    # FIXME: Error checks
    yaml_str = loads_yaml_config(config_module, config_name)
    data = yaml.load(StringIO(yaml_str))
    cfg = data.get('config')
    return cfg
