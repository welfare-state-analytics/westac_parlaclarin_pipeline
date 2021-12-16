import os

from .utility import TEST_PROTOCOLS, setup_working_folder

TEST_DATA_FOLDER = "./tests/test_data/work_folder"

# pylint: disable=unused-argument


def pytest_sessionstart(session):
    if not os.path.isdir(TEST_DATA_FOLDER):
        setup_working_folder(root_path=TEST_DATA_FOLDER, test_protocols=TEST_PROTOCOLS)
