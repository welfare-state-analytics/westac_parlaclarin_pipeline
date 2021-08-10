import os
import shutil
from os.path import join as jj
from typing import List

import pygit2
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

    shutil.rmtree(root_path, ignore_errors=True)

    speech_folder: str = jj(root_path, "riksdagen-corpus-export", "speech-xml")
    sparv_export_folder: str = jj(root_path, "riksdagen-corpus-export", "sparv-speech-xml")
    sparv_config_folder: str = jj(root_path, "sparv")
    frequency_filename: str = jj(root_path, "parla_word_frequencies.pkl")

    source_filenames: List[str] = create_test_source_repository(root_path, repository_name)
    create_test_extracted_speech_folder(speech_folder)
    create_test_sparv_folder(sparv_config_folder, speech_folder, sparv_export_folder)

    compute_term_frequencies(source=source_filenames, filename=frequency_filename)


def create_test_source_repository(
    root_path: str = DEFAULT_ROOT_PATH, repository_name: str = "riksdagen-corpus"
) -> List[str]:

    repository_folder: str = jj(root_path, repository_name)
    corpus_folder: str = jj(repository_folder, "corpus")
    source_filenames: List[str] = []

    os.makedirs(root_path, exist_ok=True)

    shutil.rmtree(repository_folder, ignore_errors=True)
    pygit2.init_repository(repository_folder, True)

    os.makedirs(corpus_folder, exist_ok=True)

    for filename in TEST_PROTOCOLS:

        year_specifier = filename.split('-')[1]
        corpus_sub_folder = jj(corpus_folder, year_specifier)
        os.makedirs(corpus_sub_folder, exist_ok=True)

        url = f'https://github.com/welfare-state-analytics/riksdagen-corpus/raw/main/corpus/{year_specifier}/{filename}'

        download_url(url, corpus_sub_folder, filename)

        source_filenames.append(jj(corpus_sub_folder, filename))

    return source_filenames


def create_test_extracted_speech_folder(
    speech_folder: str = None,
):
    speech_folder = speech_folder or jj("tests", "test_data", "work_folder", "riksdagen-corpus-export", "speech-xml")
    shutil.rmtree(speech_folder, ignore_errors=True)
    os.makedirs(speech_folder, exist_ok=True)


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
    config_filename = jj(sparv_config_folder, "config.yaml")
    os.makedirs(sparv_config_folder, exist_ok=True)
    os.makedirs(speech_folder, exist_ok=True)
    with open(config_filename, "w") as fp:
        fp.write(SPARV_CONFIG % dict(speech_folder=speech_folder, sparv_export_folder=sparv_export_folder))
