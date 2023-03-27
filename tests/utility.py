import os
import shutil
import tempfile
from glob import glob
from os import makedirs, symlink
from os.path import abspath, isdir, isfile
from os.path import join as jj
from pathlib import Path
from shutil import rmtree

from pygit2 import init_repository
from pyriksprot import compute_term_frequencies
from pyriksprot import corpus as pc
from pyriksprot import ensure_path
from pyriksprot import metadata as md
from pyriksprot import strip_extensions

RIKSPROT_SAMPLE_PROTOCOLS = [
    'prot-1936--ak--8.xml',
    'prot-1961--ak--5.xml',
    'prot-1961--fk--6.xml',
    'prot-198687--11.xml',
    'prot-200405--7.xml',
]

RIKSPROT_SAMPLE_DATA_FOLDER = "./tests/output/work_folder"


def ensure_models_folder(target_relative_folder: str):

    data_folder: str = abspath(jj(os.environ.get("RIKSPROT_DATA_FOLDER", "RIKSPROT_DATA_FOLDER_NOT_SET"), ".."))
    source_folder = abspath(jj(data_folder, target_relative_folder))
    target_folder = abspath(jj(RIKSPROT_SAMPLE_DATA_FOLDER, target_relative_folder))

    if not isdir(target_folder):
        if isdir(source_folder):
            symlink(target_folder, source_folder)


def setup_working_folder(*, tag: str, folder: str, protocols: "list[str]" = None):
    """Setup a local test data folder with minimum of necessary data and folders"""

    if not tag:
        raise ValueError("cannot proceed since current tag is unknown (RIKSPROT_REPOSITORY_TAG not set) hint: see .env")

    rmtree(folder, ignore_errors=True)
    makedirs(jj(folder, "logs"), exist_ok=True)
    makedirs(jj(folder, "annotated"), exist_ok=True)

    create_sample_xml_repository(tag=tag, protocols=protocols, root_path=folder)

    setup_work_folder_for_tagging_with_stanza(folder)

    filenames: list[str] = glob(jj(folder, "riksdagen-corpus/corpus/**/*.xml"), recursive=True)

    compute_term_frequencies(
        source=filenames,
        filename=jj(folder, "riksdagen-corpus-term-frequencies.pkl"),
        multiproc_processes=None,
    )

    Path(jj(folder, tag)).touch()


def create_sample_xml_repository(*, tag: str, protocols: "list[str]", root_path: str = RIKSPROT_SAMPLE_DATA_FOLDER):
    """Create a mimimal ParlaClarin XML git repository"""

    repository_folder: str = jj(root_path, "riksdagen-corpus")

    rmtree(repository_folder, ignore_errors=True)
    init_repository(repository_folder, True)

    download_sample_data(tag, protocols, repository_folder)


def download_sample_data(tag: str, protocols: "list[str]", repository_folder: str):
    source_folder: str = "tests/test_data/source/"
    sample_data_archive: str = jj(source_folder, f"{tag}_data.zip")
    """Create archive instead of downloading each test run"""
    if not isfile(sample_data_archive):
        download_to_archive(tag, protocols, sample_data_archive)

    """Unzip archive in repository"""
    target_folder: str = jj(repository_folder, "corpus")
    os.makedirs(target_folder, exist_ok=True)
    shutil.unpack_archive(sample_data_archive, target_folder)


def download_to_archive(tag: str, protocols: "list[str]", target_filename: str):
    with tempfile.TemporaryDirectory() as temp_folder:
        pc.download_protocols(
            filenames=protocols, target_folder=jj(temp_folder, "protocols"), create_subfolder=True, tag=tag
        )
        configs: md.MetadataTableConfigs = md.MetadataTableConfigs()
        md.gh_dl_metadata_by_config(configs=configs, tag=tag, folder=jj(temp_folder, "metadata"), force=True)

        ensure_path(target_filename)
        shutil.make_archive(strip_extensions(target_filename), 'zip', temp_folder)


def setup_work_folder_for_tagging_with_stanza(root_path: str):
    makedirs(jj(root_path, "annotated"), exist_ok=True)
    symlink("/data/sparv", jj(root_path, "sparv"))
