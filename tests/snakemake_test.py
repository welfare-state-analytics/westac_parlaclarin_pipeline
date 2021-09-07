from os import symlink
from os.path import isdir
from os.path import join as jj
from os.path import normpath as nj
from shutil import rmtree

import pytest
import snakemake
from snakemake.io import expand, glob_wildcards

from .utility import download_parla_clarin_protocols, setup_working_folder

DEFAULT_DATA_FOLDER = "/data"
TEST_DATA_FOLDER = "./tests/test_data/work_folder"


@pytest.mark.slow
def test_update_parla_clarin_test_data():

    protocols = [
        'prot-1933--fk--5.xml',
        'prot-1955--ak--22.xml',
        'prot-197879--14.xml',
        'prot-199596--35.xml',
    ]

    download_parla_clarin_protocols(protocols=protocols, target_folder='./tests/test_data/source')


def test_expand_call_arguments():
    target_folder = nj("/data/riksdagen_corpus_data/riksdagen-corpus-exports/speech_xml")
    source_folder = nj("/data/riksdagen_corpus_data/riksdagen-corpus/corpus/")
    extension = "xml"
    years, basenames = glob_wildcards(jj(source_folder, "{year}", f"{{file}}.{extension}"))

    filenames = expand(jj(target_folder, '{year}', f'{{basename}}.{extension}'), zip, year=years, basename=basenames)

    assert len(filenames) == len(years)


def ensure_models_folder(target_relative_folder: str):

    source_folder = jj(DEFAULT_DATA_FOLDER, target_relative_folder)
    target_folder = jj(TEST_DATA_FOLDER, target_relative_folder)

    if not isdir(target_folder):
        if isdir(source_folder):
            symlink(target_folder, source_folder)


# @pytest.mark.skip(reason="slow and open /etc/stdin raises error in vscode")
def test_snakemake_execute():

    work_folder = "./tests/test_data/work_folder"

    rmtree(work_folder, ignore_errors=True)

    setup_working_folder(root_path=work_folder)

    snakefile = jj('workflow', 'Snakefile')
    snakemake_args = {"workdir": "."}
    config = dict(config_filename="./tests/test_data/test_config.yml")

    success = snakemake.snakemake(
        snakefile, config=config, debug=False, **snakemake_args, keep_target_files=True, cores=1
    )

    assert success
