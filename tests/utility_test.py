from pathlib import Path
from workflow import config as config_module
from workflow.model.utility import load_yaml_config, temporary_file


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
