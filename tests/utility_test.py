import os
import sys

from workflow import config as config_module
from workflow.model.utility import load_yaml_config

sys.path.append((lambda d: os.path.join(os.getcwd().split(d)[0], d))("westac_parlaclarin_pipeline"))


def test_load_yaml_config():
    config = load_yaml_config("workflow.config", "config.yml")
    assert isinstance(config, dict)

    config = load_yaml_config(config_module, "config.yml")
    assert isinstance(config, dict)
