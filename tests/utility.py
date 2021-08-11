from os import makedirs
from os.path import join as jj
from shutil import rmtree
from typing import List

from pygit2 import init_repository
from workflow.model.term_frequency import compute_term_frequencies
from workflow.model.utility import download_url

TEST_PROTOCOLS = [
    'prot-1936--ak--8.xml',
    'prot-1961--ak--5.xml',
    'prot-1961--fk--6.xml',
    'prot-198687--11.xml',
    'prot-200405--7.xml',
]

DEFAULT_ROOT_PATH = jj("tests", "test_data", "work_folder")


def create_data_testbench(root_path: str = DEFAULT_ROOT_PATH, repository_name: str = "riksdagen-corpus"):
    """Setup a local test data folder with minimum of necessary data and folders"""
    rmtree(root_path, ignore_errors=True)

    """Target folder for extracted speeches"""
    speech_folder: str = jj(root_path, "riksdagen-corpus-export", "speech-xml")

    """Target folder for extracted XML speeches"""
    sparv_export_folder: str = jj(root_path, "riksdagen-corpus-export", "sparv-speech-xml")

    """Target folder for PoS tagged speeches"""
    sparv_config_folder: str = jj(root_path, "sparv")

    """Target filename for term frequencies (used by dehyphen module)"""
    frequency_filename: str = jj(root_path, "riksdagen-corpus-term-frequencies.pkl")

    """Create fake Git repository"""
    source_filenames: List[str] = create_test_source_repository(root_path, repository_name)

    """Create fake Git repository"""
    create_test_extracted_speech_folder(speech_folder)

    create_test_sparv_folder(sparv_config_folder, speech_folder, sparv_export_folder)

    compute_term_frequencies(source=source_filenames, filename=frequency_filename)


def create_test_source_repository(
    root_path: str = DEFAULT_ROOT_PATH, repository_name: str = "riksdagen-corpus"
) -> List[str]:
    """Create a mimimal ParlaClarin XML Git repository"""

    repository_folder: str = jj(root_path, repository_name)
    corpus_folder: str = jj(repository_folder, "corpus")
    source_filenames: List[str] = []

    makedirs(root_path, exist_ok=True)
    rmtree(repository_folder, ignore_errors=True)
    init_repository(repository_folder, True)
    makedirs(corpus_folder, exist_ok=True)

    for filename in TEST_PROTOCOLS:

        year_specifier = filename.split('-')[1]
        corpus_sub_folder = jj(corpus_folder, year_specifier)

        makedirs(corpus_sub_folder, exist_ok=True)

        url = f'https://github.com/welfare-state-analytics/riksdagen-corpus/raw/main/corpus/{year_specifier}/{filename}'

        download_url(url, corpus_sub_folder, filename)

        source_filenames.append(jj(corpus_sub_folder, filename))

    return source_filenames


def create_test_extracted_speech_folder(
    speech_folder: str = None,
):
    """Create folder tree for extracted speech XML files"""
    speech_folder = speech_folder or jj("tests", "test_data", "work_folder", "riksdagen-corpus-export", "speech-xml")
    rmtree(speech_folder, ignore_errors=True)
    makedirs(speech_folder, exist_ok=True)


SPARV_CONFIG = """
metadata:
  id: riksdagens-korpus
  language: swe
  name:
    eng: Riksdagens korpus

import:
  importer: xml_import:parse
  source_dir: %(speech_folder)s
  document_annotation: speech

xml_import:
  skip:
  - protocol:xmlns

export:
  annotations:
  - <token>:saldo.baseform
  - <token>:stanza.msd
  - <token>:stanza.pos
  default: # `sparv run` defaults
      - xml_export:pretty
      - csv_export:csv
  remove_module_namespaces: true
  scramble_on: <sentence>
  word: <token:word>

csv_export:
  annotations:
      - <token>:saldo.baseform
      - <token>:stanza.msd
      - <token>:stanza.pos
  delimiter: "\t"

segment:
    paragraph_chunk: <speech>
    paragraph_segmenter: blanklines
    sentence_chunk: <speech>
"""


def create_test_sparv_folder(sparv_config_folder: str, speech_folder: str, sparv_export_folder: str):
    """Write a default Sparv config file (NOT USED)"""
    config_filename = jj(sparv_config_folder, "config.yaml")
    makedirs(sparv_config_folder, exist_ok=True)
    makedirs(speech_folder, exist_ok=True)
    with open(config_filename, "w") as fp:
        fp.write(SPARV_CONFIG % dict(speech_folder=speech_folder, sparv_export_folder=sparv_export_folder))
