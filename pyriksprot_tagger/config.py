from __future__ import annotations

import importlib
import io
import os
import time
from dataclasses import dataclass, field
from functools import cached_property
from os.path import abspath, join, normpath
from pathlib import Path

import yaml
from dotenv import load_dotenv
from pyriksprot import ITaggerFactory, dget

from .utility import sparv_datadir, stanza_dir

load_dotenv()

# pylint: disable=too-many-arguments


def nj(*paths) -> str | None:
    return normpath(join(*paths)) if not None in paths else None


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

    @property
    def folder(self) -> str:
        return nj(self.repository_folder, "corpus/protocols")

    @property
    def parent_folder(self) -> str:
        return abspath(nj(self.repository_folder, '..'))


@dataclass
class TargetConfig:
    folder: str
    extension: str = field(default="xml")


@dataclass
class DehyphenConfig:
    folder: str
    tf_filename: str


@dataclass
class ExtractConfig:
    folder: str
    template: str = field(default="")
    extension: str = field(default="xml")


class Config:
    def __init__(
        self,
        data_folder: str,
        source_opts: SourceConfig = None,
        target_opts: TargetConfig = None,
        extract_opts: ExtractConfig = None,
        dehyphen_opts: DehyphenConfig = None,
        tagger_module: str = None,
        tagger_opts: dict = field(default_factory=dict),
    ):
        self.data_folder: str = nj(data_folder)
        self.source: SourceConfig = source_opts
        self.target: TargetConfig = target_opts
        self.extract: ExtractConfig = extract_opts
        self.dehyphen: DehyphenConfig = dehyphen_opts
        self.tagger_module: str | None = tagger_module
        self.tagger_opts: dict = tagger_opts or {}

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
                folder=nj(dget(data, "target_folder", "target.folder")),
                extension=dget(data, "target_extension", "target.extension", default="zip"),
            ),
            source_opts=SourceConfig(
                repository_folder=dget(
                    data, "repository.folder", "repository_folder", default=nj(data_folder, "riksdagen-corpus")
                ),
                repository_tag=dget(
                    data, "tag", "repository.tag", "repository_tag", default=os.environ.get("RIKSPROT_REPOSITORY_TAG")
                ),
            ),
            extract_opts=ExtractConfig(
                folder=nj(dget(data, "export.folder", "export_folder")),
                template=dget(data, "export.template", "export_template"),
                extension=dget(data, "export.extension", "export_extension"),
            ),
            dehyphen_opts=DehyphenConfig(
                folder=dget(data, "dehyphen_folder", "dehyphen.folder", default=data_folder),
                tf_filename=dget(
                    data, "tf_filename", "dehyphen.tf_filename", default=nj(data_folder, "word-frequencies.pkl")
                ),
            ),
            tagger_module=dget(data, "tagger_module"),
            tagger_opts=dget(data, "tagger_opts")
            if "tagger_opts" in data
            else {k.lstrip("tagger_"): v for k, v in data.items() if k.startswith("tagger_") and k != "tegger_module"},
        )

    @cached_property
    def stanza_dir(self):
        return stanza_dir(self.data_folder)

    @cached_property
    def sparv_datadir(self):
        return sparv_datadir(self.data_folder)

    @cached_property
    def log_folder(self):
        return nj(self.data_folder, "logs")

    @cached_property
    def log_filename(self):
        return nj(self.log_folder, f'parla_clarin_{time.strftime("%Y%m%d%H%M")}.log')

    @cached_property
    def tagger_factory(self) -> ITaggerFactory:
        if self.tagger_module is None:
            return None
        tagger_module = importlib.import_module(self.tagger_module)
        abstract_factory = getattr(tagger_module, "tagger_factory")
        if abstract_factory is None:
            raise ValueError(f"Module {self.tagger_module} does not implement `tagger_factory`.")
        return abstract_factory(self)
