from glob import glob
from os import makedirs, symlink
from os.path import join as jj
from shutil import rmtree
from typing import List

from pygit2 import init_repository
from pyriksprot import compute_term_frequencies, download_metadata, download_protocols

GITHUB_SOURCE_URL = "https://github.com/welfare-state-analytics/riksdagen-corpus/raw/main/corpus"

TEST_PROTOCOLS = [
    'prot-1936--ak--8.xml',
    'prot-1961--ak--5.xml',
    'prot-1961--fk--6.xml',
    'prot-198687--11.xml',
    'prot-200405--7.xml',
]

DEFAULT_ROOT_PATH = jj("tests", "test_data", "work_folder")


def setup_working_folder(root_path: str = DEFAULT_ROOT_PATH, test_protocols: List[str] = None):
    """Setup a local test data folder with minimum of necessary data and folders"""

    test_protocols: List[str] = test_protocols or TEST_PROTOCOLS

    rmtree(root_path, ignore_errors=True)
    makedirs(root_path, exist_ok=True)

    makedirs(jj(root_path, "logs"), exist_ok=True)
    makedirs(jj(root_path, "annotated"), exist_ok=True)

    create_sample_xml_repository(protocols=test_protocols, root_path=root_path, tag="main")

    # setup_work_folder_for_tagging_with_sparv(root_path)

    setup_work_folder_for_tagging_with_stanza(root_path)

    source_filenames: List[str] = glob(jj(root_path, "riksdagen-corpus/corpus/**/*.xml"), recursive=True)
    compute_term_frequencies(
        source=source_filenames,
        filename=jj(root_path, "riksdagen-corpus-term-frequencies.pkl"),
        multiproc_processes=None,
    )


def create_sample_xml_repository(*, protocols: List[str], root_path: str = DEFAULT_ROOT_PATH, tag: str = "main"):
    """Create a mimimal ParlaClarin XML git repository"""

    repository_folder: str = jj(root_path, "riksdagen-corpus")
    target_folder: str = jj(repository_folder, "corpus")

    rmtree(repository_folder, ignore_errors=True)
    init_repository(repository_folder, True)

    download_protocols(
        protocols=protocols, target_folder=jj(target_folder, "protocols"), create_subfolder=True, tag=tag
    )
    download_metadata(target_folder=jj(target_folder, "metadata"), tag=tag)


def setup_work_folder_for_tagging_with_stanza(root_path: str):
    makedirs(jj(root_path, "annotated"), exist_ok=True)
    symlink("/data/sparv", jj(root_path, "sparv"))


# @deprecated
# def setup_work_folder_for_tagging_with_sparv(root_path: str):
#     """Write a default Sparv config file (NOT USED)"""

#     """Target folder for extracted speeches"""
#     speech_folder: str = jj(root_path, "riksdagen-corpus-export", "speech-xml")

#     """Create target folder for extracted speeches"""
#     rmtree(speech_folder, ignore_errors=True)
#     makedirs(speech_folder, exist_ok=True)

#     """Target folder for PoS tagged speeches"""

#     makedirs(speech_folder, exist_ok=True)

#     makedirs(jj(root_path, "sparv"), exist_ok=True)

#     shutil.copyfile("tests/test_data/sparv_config.yml", jj(root_path, "sparv", "config.yaml"))
