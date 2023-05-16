import os
from os.path import isdir

from dotenv import load_dotenv

from .utility import RIKSPROT_SAMPLE_DATA_FOLDER, RIKSPROT_SAMPLE_PROTOCOLS, setup_working_folder


def pytest_sessionstart(session):  # pylint: disable=unused-argument
    load_dotenv()

    tag: str = os.environ.get("RIKSPROT_REPOSITORY_TAG")

    setup_working_folder(tag=tag, folder=RIKSPROT_SAMPLE_DATA_FOLDER, protocols=RIKSPROT_SAMPLE_PROTOCOLS)

    if not isdir(RIKSPROT_SAMPLE_DATA_FOLDER):
        raise ValueError("setup failed: sample folder does not exist")
