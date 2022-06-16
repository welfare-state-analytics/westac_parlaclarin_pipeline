from io import StringIO
from os.path import join as jj
from os.path import normpath as nj
from pathlib import Path

import yaml

from workflow.config import Config
from workflow.utility import temporary_file


def test_temporary_file():

    filename = jj("tests", "output", "trazan.txt")

    with temporary_file(filename=filename) as path:
        path.touch()
        assert path.is_file(), "file doesn't exists"
    assert not Path(filename).is_file(), "file exists"

    with temporary_file(filename=filename, content="X") as path:
        assert path.is_file(), "file doesn't exists"
        with open(filename, "r", encoding="utf-8") as fp:
            assert fp.read() == "X"
    assert not Path(filename).is_file(), "file exists"

    with temporary_file(filename=None, content="X") as path:
        filename = str(path)
        assert path.is_file(), "file doesn't exists"
        with open(filename, "r", encoding="utf-8") as fp:
            assert fp.read() == "X"
    assert not Path(filename).is_file(), "file exists"


yaml_str = """

work_folders: !work_folders &work_folders
  data_folder: /home/roger/data

parla_clarin: !parla_clarin &parla_clarin
  repository_folder: /data/westac/riksdagen_corpus_data/riksdagen-corpus
  repository_url: https://github.com/welfare-state-analytics/riksdagen-corpus.git
  repository_branch: main
  folder: /home/roger/source/welfare-state-analytics/westac_parlaclarin_pipeline/sandbox/test-parla-clarin/source
  # folder: /data/westac/riksdagen_corpus_data/riksdagen-corpus/data/new-parlaclarin

extract_speeches: !extract_speeches &extract_speeches
  folder: /home/roger/source/welfare-state-analytics/westac_parlaclarin_pipeline/sandbox/test-speech-xml/source
  template: speeches.cdata.xml
  extension: xml

word_frequency: !word_frequency &word_frequency
  <<: *work_folders
  filename: riksdagen-corpus-term-frequencies.pkl

dehyphen: !dehyphen &dehyphen
  <<: *work_folders
  whitelist_filename: dehyphen_whitelist.txt.gz
  whitelist_log_filename: dehyphen_whitelist_log.pkl
  unresolved_filename: dehyphen_unresolved.txt.gz

config: !config
    work_folders: *work_folders
    parla_clarin: *parla_clarin
    extract_speeches: *extract_speeches
    word_frequency: *word_frequency
    dehyphen: *dehyphen
    annotated_folder: /home/roger/data/annotated
    stanza_folder: /data/sparv/models/stanza

"""

simple_yaml_str: str = """
root_folder: /home/roger/data
target_folder: /home/roger/data/annotated
repository_folder: /home/roger/data/riksdagen-corpus
repository_branch: v0.4.5
source_folder: /home/roger/data/riksdagen-corpus/corpus/protocols/1936
"""


def test_simple_import_yaml():
    config: Config = Config.load(simple_yaml_str)
    assert isinstance(config, Config)

    # config = config.normalize()

    assert config.work_folders.data_folder == nj("/home/roger/data")
    assert config.dehyphen.data_folder == nj("/home/roger/data")
    assert config.word_frequency.data_folder == nj("/home/roger/data")
    assert config.parla_clarin.repository_url == "https://github.com/welfare-state-analytics/riksdagen-corpus.git"
    assert config.parla_clarin.repository_branch == "v0.4.5"

    # assert config.extract_speeches.template == "speeches.cdata.xml"


def test_import_yaml():
    data = yaml.full_load(StringIO(yaml_str))
    assert isinstance(data, dict)
    config: Config = data.get('config')
    config = config.normalize()

    assert isinstance(config, Config)

    assert config.work_folders.data_folder == nj("/home/roger/data")
    assert config.dehyphen.data_folder == nj("/home/roger/data")
    assert config.word_frequency.data_folder == nj("/home/roger/data")
    assert config.extract_speeches.template == "speeches.cdata.xml"
    assert config.parla_clarin.repository_url == "https://github.com/welfare-state-analytics/riksdagen-corpus.git"
    assert config.parla_clarin.repository_branch == "main"


def test_load_typed_config():
    config: Config = Config.load("config.yml")
    assert isinstance(config, Config)
    config: Config = Config.load("test_config.yml")
    assert isinstance(config, Config)


bug_yaml_str = """work_folders: !work_folders &work_folders
  data_folder: tests/output/work_folder

parla_clarin: !parla_clarin &parla_clarin
  repository_folder: tests/output/work_folder/riksdagen-corpus
  repository_url: https://github.com/welfare-state-analytics/riksdagen-corpus.git
  repository_branch: main
  folder: tests/output/work_folder/riksdagen-corpus/corpus/protocols

extract_speeches: !extract_speeches &extract_speeches
  folder: tests/output/work_folder/riksdagen-corpus-export/speech-xml
  template: speeches.cdata.xml
  extension: xml

word_frequency: !word_frequency &word_frequency
  <<: *work_folders
  filename: riksdagen-corpus-term-frequencies.pkl

dehyphen: !dehyphen &dehyphen
  <<: *work_folders
  whitelist_filename: dehyphen_whitelist.txt.gz
  whitelist_log_filename: dehyphen_whitelist_log.pkl
  unresolved_filename: dehyphen_unresolved.txt.gz

config: !config
    work_folders: *work_folders
    parla_clarin: *parla_clarin
    extract_speeches: *extract_speeches
    word_frequency: *word_frequency
    dehyphen: *dehyphen
    annotated_folder: tests/output/annotated
    stanza_folder: /data/sparv/models/stanza
"""


