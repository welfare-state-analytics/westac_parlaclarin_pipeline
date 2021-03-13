import os
import shutil

import pygit2
from workflow.model.utility import download_url

TEST_PROTOCOLS = [
    'prot-1936--ak--8.xml',
    'prot-1961--ak--5.xml',
    'prot-1961--fk--6.xml',
    'prot-198687--11.xml',
    'prot-200405--7.xml',
]


def create_data_testbench(root_path: str = "tests/test_data/work_folder", repository_name: str = "riksdagen-corpus"):
    speech_folder: str = os.path.join(root_path, "riksdagens-corpus-export/speech-xml")
    sparv_export_folder: str = os.path.join(root_path, "riksdagens-corpus-export/sparv-speech-xml")
    sparv_config_folder: str = os.path.join(root_path, "riksdagens-corpus-export/sparv")
    create_test_source_repository(root_path, repository_name)
    create_test_extracted_speech_folder(speech_folder)
    create_test_sparv_folder(sparv_config_folder, speech_folder, sparv_export_folder)


def create_test_source_repository(
    root_path: str = "tests/test_data/work_folder", repository_name: str = "riksdagen-corpus"
):

    repository_folder: str = os.path.join(root_path, repository_name)
    corpus_folder: str = os.path.join(repository_folder, "corpus")

    shutil.rmtree(repository_folder, ignore_errors=True)
    pygit2.init_repository(repository_folder, True)
    os.makedirs(corpus_folder, exist_ok=True)

    for filename in TEST_PROTOCOLS:

        year_specifier = filename.split('-')[1]
        corpus_sub_folder = os.path.join(corpus_folder, year_specifier)
        os.makedirs(corpus_sub_folder, exist_ok=True)

        url = f'https://github.com/welfare-state-analytics/riksdagen-corpus/raw/main/corpus/{year_specifier}/{filename}'

        download_url(url, corpus_sub_folder, filename)


def create_test_extracted_speech_folder(
    speech_folder: str = "tests/test_data/work_folder/riksdagens-corpus-export/speech-xml",
):
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
  export_path:
  - %(sparv_export_folder)s

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
    config_filename = os.path.join(sparv_config_folder, "config.yml")
    os.makedirs(sparv_config_folder, exist_ok=True)
    os.makedirs(speech_folder, exist_ok=True)
    with open(config_filename, "w") as fp:
        fp.write(SPARV_CONFIG % dict(speech_folder=speech_folder, sparv_export_folder=sparv_export_folder))
