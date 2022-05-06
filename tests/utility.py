import os
from glob import glob
from os import makedirs, symlink
from os.path import abspath, isdir
from os.path import join as jj
from pathlib import Path
from shutil import rmtree
from typing import List

from pygit2 import init_repository
from pyriksprot import compute_term_frequencies, download_protocols, metadata

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


def setup_working_folder(
    *,
    tag: str,
    root_path: str = RIKSPROT_SAMPLE_DATA_FOLDER,
    test_protocols: List[str] = None,
):
    """Setup a local test data folder with minimum of necessary data and folders"""

    test_protocols: List[str] = test_protocols or RIKSPROT_SAMPLE_PROTOCOLS

    rmtree(root_path, ignore_errors=True)
    makedirs(root_path, exist_ok=True)

    makedirs(jj(root_path, "logs"), exist_ok=True)
    makedirs(jj(root_path, "annotated"), exist_ok=True)

    create_sample_xml_repository(tag=tag, protocols=test_protocols, root_path=root_path)

    setup_work_folder_for_tagging_with_stanza(root_path)

    source_filenames: List[str] = glob(jj(root_path, "riksdagen-corpus/corpus/**/*.xml"), recursive=True)

    compute_term_frequencies(
        source=source_filenames,
        filename=jj(root_path, "riksdagen-corpus-term-frequencies.pkl"),
        multiproc_processes=None,
    )

    Path(jj(root_path, tag)).touch()


def create_sample_xml_repository(
    *,
    tag: str,
    protocols: List[str],
    root_path: str = RIKSPROT_SAMPLE_DATA_FOLDER,
):
    """Create a mimimal ParlaClarin XML git repository"""

    repository_folder: str = jj(root_path, "riksdagen-corpus")
    target_folder: str = jj(repository_folder, "corpus")

    rmtree(repository_folder, ignore_errors=True)
    init_repository(repository_folder, True)

    download_protocols(
        protocols=protocols, target_folder=jj(target_folder, "protocols"), create_subfolder=True, tag=tag
    )
    metadata.download_to_folder(tag=tag, folder=jj(target_folder, "metadata"), force=True)


def setup_work_folder_for_tagging_with_stanza(root_path: str):
    makedirs(jj(root_path, "annotated"), exist_ok=True)
    symlink("/data/sparv", jj(root_path, "sparv"))
