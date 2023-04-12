from os.path import join as jj
from os.path import normpath as nj
from pathlib import Path

import pytest

from workflow.config import Config
from workflow.utility import temporary_file

TEST_DATA_FOLDER = "tests/output/data"
TEST_TAG = "v0.9.9"

SIMPLE_YAML_STR1: str = f"""
root_folder: {TEST_DATA_FOLDER}
target_folder: {TEST_DATA_FOLDER}/tagged_frames
repository_folder: /data/riksdagen-corpus
repository_tag: {TEST_TAG}
export_folder: /data/exports
export_template: /data/templates/speeches.cdata.xml
export_extension: xml
"""

SIMPLE_YAML_STR2: str = f"""
root_folder: {TEST_DATA_FOLDER}
target_folder: {TEST_DATA_FOLDER}/tagged_frames
repository:
  folder: /data/riksdagen-corpus
  tag: {TEST_TAG}
export:
  folder: /data/exports
  template: /data/templates/speeches.cdata.xml
  extension: xml
"""


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


@pytest.mark.parametrize("yaml_str", [SIMPLE_YAML_STR1, SIMPLE_YAML_STR2])
def test_load_yaml_str(yaml_str: str):

    data_folder: str = TEST_DATA_FOLDER

    config: Config = Config.load(yaml_str)
    assert isinstance(config, Config)

    assert config.data_folder == nj(data_folder)
    assert config.log_folder == f"{data_folder}/logs"
    assert config.log_filename == jj(config.log_folder, config.log_basename)

    assert config.source.repository_url == "https://github.com/welfare-state-analytics/riksdagen-corpus.git"
    assert config.source.repository_folder == "/data/riksdagen-corpus"
    assert config.source.repository_tag == TEST_TAG
    assert config.source.folder == "/data/riksdagen-corpus/corpus/protocols"

    assert config.extract.folder == "/data/exports"
    assert config.extract.template == "/data/templates/speeches.cdata.xml"
    assert config.extract.extension == "xml"

    assert config.dehyphen.folder == nj(data_folder)
    assert config.dehyphen.tf_filename == jj(data_folder, "riksdagen-corpus-term-frequencies.pkl")
