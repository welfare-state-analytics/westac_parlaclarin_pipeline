import glob
from os import environ, makedirs, symlink
from os.path import abspath as aj
from os.path import isdir, isfile
from os.path import join as jj
from os.path import normpath as nj
from shutil import rmtree
from typing import List

import pytest
import snakemake
from snakemake.io import expand, glob_wildcards

from workflow.config import Config, load_typed_config
from workflow.utility import strip_path_and_extension

from .utility import create_sample_xml_repository, setup_work_folder_for_tagging_with_stanza

DEFAULT_DATA_FOLDER = "/data"
TEST_DATA_FOLDER = "./tests/test_data/work_folder"


@pytest.mark.skipif(environ.get("CORPUS_REPOSITORY_FOLDER") is None, reason="no data")
def test_expand_call_arguments():

    source_folder = jj(environ["CORPUS_REPOSITORY_FOLDER"], "protocols")
    target_folder = nj("/data/westac/riksdagen_corpus_data/riksdagen-corpus-exports/speech_xml")
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


@pytest.mark.slow
# @pytest.mark.skip(reason="Very slow")
def test_snakemake_execute():

    config_filename = aj("./tests/test_data/test_config.yml")

    cfg: Config = load_typed_config(config_name=config_filename)

    snakefile = jj('workflow', 'Snakefile')

    rmtree(cfg.annotated_folder, ignore_errors=True)
    makedirs(cfg.annotated_folder, exist_ok=True)

    success = snakemake.snakemake(
        snakefile,
        config=dict(config_filename=config_filename),
        debug=True,
        # workdir=workdir,
        keep_target_files=True,
        cores=1,
        verbose=True,
    )

    assert success

    source_files: List[str] = glob.glob(
        jj(cfg.data_folder, 'riksdagen-corpus/corpus/protocols/**/prot*.xml'), recursive=True
    )

    for filename in source_files:

        document_name: str = strip_path_and_extension(filename)
        target_dir: str = jj(cfg.annotated_folder, document_name.split('-')[1])

        assert isfile(jj(target_dir, f"{document_name}.zip"))


@pytest.mark.slow
def test_snakemake_word_frequency():

    protocols: List[str] = [
        'prot-1936--ak--8.xml',
        'prot-197778--160.xml',
    ]

    workdir = aj("./tests/output/work_folder")
    config_filename = aj("./tests/test_data/test_config_output.yml")

    rmtree(workdir, ignore_errors=True)
    makedirs(workdir, exist_ok=True)
    makedirs(jj(workdir, "logs"), exist_ok=True)

    create_sample_xml_repository(protocols=protocols, root_path=workdir, tag="main")
    setup_work_folder_for_tagging_with_stanza(workdir)

    snakefile = jj('workflow', 'Snakefile')

    snakemake.snakemake(
        snakefile,
        config=dict(config_filename=config_filename, processes=4),
        debug=True,
        # workdir=workdir,
        keep_target_files=True,
        cores=1,
        verbose=True,
        targets=['word_frequency'],
    )

    assert isfile(jj(workdir, "riksdagen-corpus-term-frequencies.pkl"))
