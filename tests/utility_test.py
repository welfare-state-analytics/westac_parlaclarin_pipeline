from io import StringIO
from pathlib import Path

import yaml
from workflow.config import Config, load_typed_config, loads_typed_config
from workflow.model.utility import temporary_file


def test_temporary_file():

    filename = "tests/output/trazan.txt"

    with temporary_file(filename=filename) as path:
        path.touch()
        assert path.is_file(), "file doesn't exists"
    assert not Path(filename).is_file(), "file exists"

    with temporary_file(filename=filename, content="X") as path:
        assert path.is_file(), "file doesn't exists"
        with open(filename, "r") as fp:
            assert fp.read() == "X"
    assert not Path(filename).is_file(), "file exists"

    with temporary_file(filename=None, content="X") as path:
        filename = str(path)
        assert path.is_file(), "file doesn't exists"
        with open(filename, "r") as fp:
            assert fp.read() == "X"
    assert not Path(filename).is_file(), "file exists"


yaml_str = """

work_folders: !work_folders &work_folders
  data_folder: /home/roger/data

parla_clarin: !parla_clarin &parla_clarin
  repository_folder: /data/riksdagen_corpus_data/riksdagen-corpus
  repository_url: https://github.com/welfare-state-analytics/riksdagen-corpus.git
  folder: /home/roger/source/welfare-state-analytics/westac_parlaclarin_pipeline/sandbox/test-parla-clarin/source
  # folder: /data/riksdagen_corpus_data/riksdagen-corpus/data/new-parlaclarin

extract_speeches: !extract_speeches &extract_speeches
  folder: /home/roger/source/welfare-state-analytics/westac_parlaclarin_pipeline/sandbox/test-speech-xml/source
  template: speeches.cdata.xml
  extension: xml

word_frequency: !word_frequency &word_frequency
  <<: *work_folders
  filename: parla_word_frequencies.pkl

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

"""


def test_import_yaml():
    data = yaml.full_load(StringIO(yaml_str))
    assert isinstance(data, dict)
    config = data.get('config')
    assert isinstance(config, Config)
    assert config.work_folders.data_folder == "/home/roger/data"
    assert config.dehyphen.data_folder == "/home/roger/data"
    assert config.word_frequency.data_folder == "/home/roger/data"
    assert config.extract_speeches.template == "speeches.cdata.xml"
    assert config.parla_clarin.repository_url == "https://github.com/welfare-state-analytics/riksdagen-corpus.git"


def test_load_typed_config():
    config: Config = load_typed_config("config.yml")
    assert isinstance(config, Config)
    config: Config = load_typed_config("test_config.yml")
    assert isinstance(config, Config)


bug_yaml_str = """work_folders: !work_folders &work_folders
  data_folder: tests/test_data/work_folder

parla_clarin: !parla_clarin &parla_clarin
  repository_folder: tests/test_data/work_folder/riksdagen-corpus
  repository_url: https://github.com/welfare-state-analytics/riksdagen-corpus.git
  folder: tests/test_data/work_folder/riksdagen-corpus/corpus

extract_speeches: !extract_speeches &extract_speeches
  folder: tests/test_data/work_folder/riksdagen-corpus-export/speech-xml
  template: speeches.cdata.xml
  extension: xml

word_frequency: !word_frequency &word_frequency
  <<: *work_folders
  filename: parla_word_frequencies.pkl

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
"""


def test_load_typed_config_bug():
    config: Config = loads_typed_config(bug_yaml_str)
    assert isinstance(config, Config)
