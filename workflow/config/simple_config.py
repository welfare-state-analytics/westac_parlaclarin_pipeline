import io
import os
import time
from os.path import join as jj
from pathlib import Path

import yaml
from dotenv import load_dotenv
from pyriksprot import norm_join as nj

from .utility import sparv_datadir, stanza_dir

load_dotenv()


class WorkFoldersConfig:
    def __init__(self, data_folder: str) -> None:
        self.data_folder: str = nj(data_folder)

    def __repr__(self):
        return f"{self.__class__.__name__}(data_folder={self.data_folder})"

    @property
    def log_folder(self) -> str:
        return nj(self.data_folder, 'logs')


class RepositoryConfig:

    REPOSITORY_URL: str = "https://github.com/welfare-state-analytics/riksdagen-corpus.git"

    def __init__(self, repository_folder: str, repository_branch: str, folder: str = None):
        self.repository_folder: str = nj(repository_folder)
        self.repository_branch: str = repository_branch
        self.repository_url: str = self.REPOSITORY_URL
        self.folder = folder or jj(self.repository_folder, "corpus/protocols")

    def __repr__(self):
        return f"{self.__class__.__name__}(repository_folder={self.repository_folder},repository_url={self.repository_url},repository_branch={self.repository_branch},folder={self.folder})"


class WordFrequencyConfig:
    def __init__(self, data_folder: str, filename: str = "riksdagen-corpus-term-frequencies.pkl"):
        self.data_folder: str = nj(data_folder)
        self.filename: str = filename

    @property
    def fullname(self) -> str:
        return jj(self.data_folder, self.filename)

    def __repr__(self):
        return f"{self.__class__.__name__}(data_folder={self.data_folder},filename={self.filename})"

    @property
    def repository_parent_folder(self):
        return os.path.abspath(nj(self.repository_folder, '..'))


class DehyphenConfig:
    def __init__(self, data_folder: str):
        self.data_folder: str = nj(data_folder)
        self.whitelist_filename: str = jj(data_folder, "dehyphen_whitelist.txt.gz")
        self.whitelist_log_filename: str = jj(data_folder, "dehyphen_whitelist_log.pkl")
        self.unresolved_filename: str = jj(data_folder, "dehyphen_unresolved.txt.gz")

    @property
    def opts(self) -> dict:
        return dict(
            whitelist_filename=self.whitelist_filename,
            whitelist_log_filename=self.whitelist_log_filename,
            unresolved_filename=self.unresolved_filename,
        )

    def __repr__(self):
        return (
            f"{self.__class__.__name__}"
            f"whitelist_filename={self.whitelist_filename},"
            f"whitelist_log_filename={self.whitelist_log_filename},"
            f"unresolved_filename={self.unresolved_filename})"
        )


class SimpleConfig:
    def __init__(
        self,
        data_folder: str,
        target_folder: str,
        repository_branch: str,
        repository_folder: str = None,
        source_folder: str = None,
        source_extension: str = "xml",
        target_extension: str = "zip",
    ):
        self.work_folders: WorkFoldersConfig = WorkFoldersConfig(data_folder=data_folder)
        self.parla_clarin: RepositoryConfig = RepositoryConfig(
            repository_folder=repository_folder or jj(data_folder, "riksdagen-corpus"),
            repository_branch=repository_branch,
            folder=source_folder,
        )
        self.word_frequency: WordFrequencyConfig = WordFrequencyConfig(data_folder)
        self.dehyphen: DehyphenConfig = DehyphenConfig(data_folder)
        self.annotated_folder: str = target_folder
        self.source_extension: str = source_extension
        self.target_extension: str = target_extension
        self.log_name: str = f'parla_clarin_{time.strftime("%Y%m%d%H%M")}.log'

    @staticmethod
    def load(source: str) -> "SimpleConfig":
        """Load YAML configuration named `config_name` in resources folder. Return typed config."""
        if os.path.isfile(source):
            data: dict = yaml.safe_load(Path(source).read_text(encoding="utf-8"))
        else:
            data: dict = yaml.safe_load(io.StringIO(source))
        return SimpleConfig(
            data_folder=data.get("root_folder"),
            target_folder=data.get("target_folder"),
            repository_folder=data.get("repository_folder"),
            repository_branch=data.get("repository_branch"),
            source_folder=data.get("source_folder"),
        )

    @property
    def stanza_dir(self):
        return stanza_dir(self.work_folders.data_folder)

    @property
    def sparv_datadir(self):
        return sparv_datadir(self.work_folders.data_folder)
