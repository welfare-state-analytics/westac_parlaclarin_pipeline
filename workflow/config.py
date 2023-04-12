import io
import os
import time
from os.path import join as jj
from pathlib import Path

import yaml
from dotenv import load_dotenv
from pyriksprot import norm_join as nj

from .utility import dget, sparv_datadir, stanza_dir

load_dotenv()

# pylint: disable=too-many-arguments


class SafeLoaderIgnoreUnknown(yaml.SafeLoader):  # pylint: disable=too-many-ancestors
    def let_unknown_through(self, node):  # pylint: disable=unused-argument
        return None


SafeLoaderIgnoreUnknown.add_constructor(None, SafeLoaderIgnoreUnknown.let_unknown_through)


class SourceConfig:

    REPOSITORY_URL: str = "https://github.com/welfare-state-analytics/riksdagen-corpus.git"

    def __init__(self, *, repository_folder: str, repository_tag: str, extension: str = "xml"):

        if not repository_tag:
            raise ValueError("Corpus tag cannot be empty")

        self.repository_folder: str = nj(repository_folder)
        self.repository_tag: str = repository_tag
        self.repository_url: str = self.REPOSITORY_URL
        self.extension: str = extension

    def __repr__(self):
        return f"{self.__class__.__name__}(repository_folder={self.repository_folder},repository_url={self.repository_url},repository_tag={self.repository_tag},folder={self.folder},extension={self.extension})"

    @property
    def folder(self) -> str:
        return jj(self.repository_folder, "corpus/protocols")

    @property
    def parent_folder(self) -> str:
        return os.path.abspath(nj(self.repository_folder, '..'))


class TargetConfig:
    def __init__(self, folder: str, extension: str = "xml"):
        self.folder: str = nj(folder) if folder else None
        self.extension: str = extension

    def __repr__(self):
        return f"{self.__class__.__name__}(folder={self.folder},extension={self.extension})"


class DehyphenConfig:
    def __init__(self, folder: str, tf_filename: str = None):
        self.folder: str = folder
        self.tf_filename: str = tf_filename or jj(folder, "riksdagen-corpus-term-frequencies.pkl")


class ExtractConfig:
    def __init__(self, folder: str, template: str = "", extension: str = "xml"):
        self.folder: str = nj(folder) if folder else None
        self.template: str = template
        self.extension: str = extension

    def __repr__(self):
        return f"{self.__class__.__name__}(folder={self.folder},template={self.template},extension={self.extension})"


class Config:
    def __init__(
        self,
        data_folder: str,
        source_opts: SourceConfig = None,
        target_opts: TargetConfig = None,
        extract_opts: ExtractConfig = None,
        dehyphen_opts: DehyphenConfig = None,
    ):
        self.data_folder: str = nj(data_folder)
        self.source: SourceConfig = source_opts
        self.target: TargetConfig = target_opts
        self.extract: ExtractConfig = extract_opts
        self.dehyphen: DehyphenConfig = dehyphen_opts
        self.log_basename: str = f'parla_clarin_{time.strftime("%Y%m%d%H%M")}.log'

    @staticmethod
    def load(source: str) -> "Config":
        """Load YAML configuration named `config_name` in resources folder. Return typed config."""

        if source is None:
            raise ValueError("Config source cannot be None")

        if source.endswith("yml") and not os.path.isfile(source):
            raise FileNotFoundError(f"Config file {source} not found")

        data: dict = (
            yaml.load(Path(source).read_text(encoding="utf-8"), Loader=SafeLoaderIgnoreUnknown)
            if os.path.isfile(source)
            else yaml.load(io.StringIO(source), Loader=SafeLoaderIgnoreUnknown)
        )

        data_folder: str = dget(data, "data_folder", "root_folder")

        return Config(
            data_folder=data_folder,
            target_opts=TargetConfig(
                folder=dget(data, "target_folder", "target.folder"),
                extension=dget(data, "target_extension", "target.extension", default="zip"),
            ),
            source_opts=SourceConfig(
                repository_folder=dget(
                    data, "repository.folder", "repository_folder", default=jj(data_folder, "riksdagen-corpus")
                ),
                repository_tag=dget(
                    data, "tag", "repository.tag", "repository_tag", default=os.environ.get("RIKSPROT_REPOSITORY_TAG")
                ),
            ),
            extract_opts=ExtractConfig(
                folder=dget(data, "export.folder", "export_folder"),
                template=dget(data, "export.template", "export_template"),
                extension=dget(data, "export.extension", "export_extension"),
            ),
            dehyphen_opts=DehyphenConfig(
                folder=dget(data, "dehyphen_folder", "dehypen.folder", default=data_folder),
                tf_filename=dget(data, "tf_filename", "dehyphen.tf_filename", default=None),
            ),
        )

    @property
    def stanza_dir(self):
        return stanza_dir(self.data_folder)

    @property
    def sparv_datadir(self):
        return sparv_datadir(self.data_folder)

    @property
    def log_folder(self):
        return jj(self.data_folder, "logs")

    @property
    def log_filename(self):
        return jj(self.log_folder, self.log_basename)
