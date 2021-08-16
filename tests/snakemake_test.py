from os import symlink
from os.path import isdir
from os.path import join as jj
from os.path import normpath as nj
from shutil import rmtree

import pytest
import snakemake
from snakemake.io import expand, glob_wildcards

from .utility import setup_working_folder

DEFAULT_DATA_FOLDER = "/data"
TEST_DATA_FOLDER = "./tests/test_data/work_folder"


def test_expand_call_arguments():
    target_folder = nj("/data/riksdagen_corpus_data/riksdagen-corpus-exports/speech_xml")
    source_folder = nj("/data/riksdagen_corpus_data/riksdagen-corpus/corpus/")
    extension = "xml"
    years, basenames = glob_wildcards(jj(source_folder, "{year}", f"{{file}}.{extension}"))

    filenames = expand(jj(target_folder, '{year}', f'{{basename}}.{extension}'), zip, year=years, basename=basenames)

    assert len(filenames) == len(years)


@pytest.mark.slow
def test_setup_working_folder():

    root_path: str = nj("tests/test_data/work_folder")

    setup_working_folder(root_path=root_path)
    # run test: snakemake -j1 --config config_filename=test_config.yaml

    # status = snakemake.snakemake(
    #     snakefile='./workflow/Snakefile',
    #     cores=1,
    #     config={'config_filename': 'test_config.yml'},
    #     unlock=True,
    # )


def ensure_models_folder(target_relative_folder: str):

    source_folder = jj(DEFAULT_DATA_FOLDER, target_relative_folder)
    target_folder = jj(TEST_DATA_FOLDER, target_relative_folder)

    if not isdir(target_folder):
        if isdir(source_folder):
            symlink(target_folder, source_folder)


@pytest.mark.skip(reason="slow and open /etc/stdin raises error in vscode")
def test_snakemake_execute():

    work_folder = "./tests/test_data/work_folder"

    rmtree(work_folder, ignore_errors=True)

    setup_working_folder(root_path=work_folder)

    snakefile = jj('workflow', 'Snakefile')
    snakemake_args = {"workdir": "."}
    config = dict(config_filename="./tests/test_data/test_config.yml")

    success = snakemake.snakemake(
        snakefile, config=config, debug=True, **snakemake_args, keep_target_files=True, cores=1
    )

    assert success
