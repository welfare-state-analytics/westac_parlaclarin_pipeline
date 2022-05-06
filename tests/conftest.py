import os
from os.path import isdir, isfile, join
import shutil
from .utility import RIKSPROT_SAMPLE_PROTOCOLS, RIKSPROT_SAMPLE_DATA_FOLDER, setup_working_folder
from dotenv import load_dotenv

# pylint: disable=unused-argument


def pytest_sessionstart(session):

    load_dotenv()

    tag: str = os.environ.get("RIKSPROT_REPOSITORY_TAG")

    if not tag:
        raise ValueError("cannot proceed since current tag is unknown (RIKSPROT_REPOSITORY_TAG not set) hint: see .env")

    must_update: bool = not isdir(RIKSPROT_SAMPLE_DATA_FOLDER) or not isfile(join(RIKSPROT_SAMPLE_DATA_FOLDER, tag))

    if must_update:

        shutil.rmtree(RIKSPROT_SAMPLE_DATA_FOLDER, ignore_errors=True)

        setup_working_folder(tag=tag, root_path=RIKSPROT_SAMPLE_DATA_FOLDER, test_protocols=RIKSPROT_SAMPLE_PROTOCOLS)
