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


class ParlaClarinConfig:

    REPOSITORY_URL: str = "https://github.com/welfare-state-analytics/riksdagen-corpus.git"

    def __init__(self, *, repository_folder: str, repository_tag: str, folder: str = None):
        self.repository_folder: str = nj(repository_folder)
        self.repository_tag: str = repository_tag
        self.repository_url: str = self.REPOSITORY_URL
        self.source_folder: str = folder or jj(self.repository_folder, "corpus/protocols")

    def __repr__(self):
        return f"{self.__class__.__name__}(repository_folder={self.repository_folder},repository_url={self.repository_url},repository_tag={self.repository_tag},folder={self.source_folder})"

    @property
    def parent_folder(self):
        return os.path.abspath(nj(self.repository_folder, '..'))


class TransformedSpeechesConfig:
    def __init__(self, folder: str, template: str = "", extension: str = "xml"):
        self.folder: str = nj(folder) if folder else None
        self.template: str = template
        self.extension: str = extension

    def __repr__(self):
        return f"{self.__class__.__name__}(folder={self.folder},template={self.template},extension={self.extension})"


class WordFrequencyConfig:
    def __init__(self, data_folder: str):
        self.data_folder: str = nj(data_folder)
        self.basename: str = "riksdagen-corpus-term-frequencies.pkl"

    @property
    def filename(self) -> str:
        return jj(self.data_folder, self.basename)

    def __repr__(self):
        return f"{self.__class__.__name__}(data_folder={self.data_folder},filename={self.basename})"


class DehyphenConfig:
    def __init__(self, data_folder: str):
        self.data_folder: str = nj(data_folder)
        self.whitelist_filename: str = jj(data_folder, "dehyphen_whitelist.txt.gz")
        self.whitelist_log_filename: str = jj(data_folder, "dehyphen_whitelist_log.pkl")
        self.unresolved_filename: str = jj(data_folder, "dehyphen_unresolved.txt.gz")

    def __repr__(self):
        return (
            f"{self.__class__.__name__}"
            f"(data_folder={self.data_folder},"
            f"whitelist_filename={self.whitelist_filename},"
            f"whitelist_log_filename={self.whitelist_log_filename},"
            f"unresolved_filename={self.unresolved_filename})"
        )

    @property
    def opts(self) -> dict:
        return dict(
            whitelist_filename=self.whitelist_filename,
            whitelist_log_filename=self.whitelist_log_filename,
            unresolved_filename=self.unresolved_filename,
        )


class Config:
    def __init__(
        self,
        data_folder: str,
        target_folder: str,
        parla_opts: ParlaClarinConfig = None,
        source_extension: str = "xml",
        target_extension: str = "zip",
        extract_opts: TransformedSpeechesConfig = None,
        dehyphen_opts: DehyphenConfig = None,
        tf_opts: WordFrequencyConfig = None,
    ):
        self.data_folder: str = nj(data_folder)
        self.tagged_frames_folder: str = target_folder
        self.source_extension: str = source_extension
        self.target_extension: str = target_extension

        self.corpus: ParlaClarinConfig = parla_opts
        self.extract_opts: TransformedSpeechesConfig = extract_opts
        self.tf_opts: WordFrequencyConfig = tf_opts
        self.dehyphen: DehyphenConfig = dehyphen_opts

        self.log_basename: str = f'parla_clarin_{time.strftime("%Y%m%d%H%M")}.log'

    @staticmethod
    def load(source: str) -> "Config":
        """Load YAML configuration named `config_name` in resources folder. Return typed config."""

        data: dict = (
            yaml.load(Path(source).read_text(encoding="utf-8"), Loader=SafeLoaderIgnoreUnknown)
            if os.path.isfile(source)
            else yaml.load(io.StringIO(source), Loader=SafeLoaderIgnoreUnknown)
        )

        data_folder: str = dget(data, "data_folder", "root_folder")
        repository_tag: str = dget(data, "repository.tag", "repository_tag") or os.environ.get(
            "RIKSPROT_REPOSITORY_TAG"
        )

        if not repository_tag:
            raise ValueError(
                "Corpus tag not found. Looked in (config: repository.tag, repository_tag, environ: RIKSPROT_REPOSITORY_TAG)"
            )

        repository_folder: str = dget(data, "repository.folder", "repository_folder") or jj(
            data_folder, "riksdagen-corpus"
        )
        parla_folder: str = dget(data, "repository.source_folder", "source_folder") or jj(
            repository_folder, "corpus/protocols"
        )

        parla_opts: ParlaClarinConfig = ParlaClarinConfig(
            repository_folder=repository_folder,
            repository_tag=repository_tag,
            folder=parla_folder,
        )
        extract_opts: TransformedSpeechesConfig = TransformedSpeechesConfig(
            folder=dget(data, "export.folder", "export_folder"),
            template=dget(data, "export.template", "export_template"),
            extension=dget(data, "export.extension", "export_extension"),
        )
        dehyphen_opts: DehyphenConfig = DehyphenConfig(data_folder)
        tf_opts: WordFrequencyConfig = WordFrequencyConfig(data_folder)
        target_folder: str = dget(data, "target_folder", "target.folder")
        return Config(
            data_folder=data_folder,
            target_folder=target_folder,
            parla_opts=parla_opts,
            extract_opts=extract_opts,
            dehyphen_opts=dehyphen_opts,
            tf_opts=tf_opts,
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
