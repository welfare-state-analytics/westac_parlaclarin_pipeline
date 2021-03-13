from io import StringIO
from pathlib import Path
from workflow import config as config_module
from workflow.model.utility import load_yaml_config, temporary_file
from workflow.config.typed_config import Config, load_typed_config

def test_load_yaml_config():
    config = load_yaml_config("workflow.config", "config.yml")
    assert isinstance(config, dict)

    config = load_yaml_config(config_module, "config.yml")
    assert isinstance(config, dict)


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


import yaml

yaml_str = """

work_folders: !work_folders &work_folders
  data_folder: /home/roger/data

parla_clarin: !parla_clarin &parla_clarin
  repository_folder: /data/riksdagen_corpus_data/riksdagen-corpus
  repository_url: https://github.com/welfare-state-analytics/riksdagen-corpus.git
  folder: /home/roger/source/welfare-state-analytics/westac_parlaclarin_pipeline/sandbox/test-parla-clarin/source
  # folder: /data/riksdagen_corpus_data/riksdagen-corpus/data/new-parlaclarin

transformed_speeches: !transformed_speeches &transformed_speeches
  # folder: /data/riksdagen_corpus_data/riksdagen-corpus-exports/speech_xml
  folder: /home/roger/source/welfare-state-analytics/westac_parlaclarin_pipeline/sandbox/test-speeches-xml/source
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
    transformed_speeches: *transformed_speeches
    word_frequency: *word_frequency
    dehyphen: *dehyphen

"""

def test_import_yaml():
    data = yaml.load(StringIO(yaml_str))
    assert isinstance(data, dict)
    config = data.get('config')
    assert isinstance(config, Config)
    assert config.work_folders.data_folder == "/home/roger/data"

def test_load_typed_config():
    config: Config = load_typed_config("config.yml")
    assert isinstance(config, Config)