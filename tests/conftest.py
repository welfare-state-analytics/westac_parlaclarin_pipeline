import os

from .utility import RIKSPROT_SAMPLE_PROTOCOLS, RIKSPROT_SAMPLE_DATA_FOLDER, setup_working_folder

# pylint: disable=unused-argument


def pytest_sessionstart(session):
    if not os.path.isdir(RIKSPROT_SAMPLE_DATA_FOLDER):
        setup_working_folder(root_path=RIKSPROT_SAMPLE_DATA_FOLDER, test_protocols=RIKSPROT_SAMPLE_PROTOCOLS)
