from os import makedirs, symlink
from os.path import abspath as aj
from os.path import isdir, isfile
from os.path import join as jj
from os.path import normpath as nj
from shutil import rmtree
from typing import List

import pytest
import snakemake
from pyriksprot import ITagger
from snakemake.io import expand, glob_wildcards
from workflow.config import Config, load_typed_config
from workflow.taggers import StanzaTagger, TaggerRegistry
from workflow.utility import strip_path_and_extension

from .utility import (
    TEST_PROTOCOLS,
    download_parla_clarin_protocols,
    setup_parla_clarin_repository,
    setup_work_folder_for_tagging_with_stanza,
    setup_working_folder,
)

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


def test_tagger_registry_get():
    config_filename: str = aj("./tests/test_data/test_config.yml")
    cfg: Config = load_typed_config(config_filename)
    dehyphen_opts = dict(word_frequency_filename=cfg.word_frequency.fullname, **cfg.dehyphen.opts)
    tagger: ITagger = TaggerRegistry.get(
        tagger_cls=StanzaTagger,
        model=cfg.stanza_dir,
        dehyphen_opts=dehyphen_opts,
        use_gpu=False,
    )
    assert isinstance(tagger, StanzaTagger)

    tagger2: ITagger = TaggerRegistry.get(
        tagger_cls=StanzaTagger,
        model=cfg.stanza_dir,
        dehyphen_opts=dehyphen_opts,
        use_gpu=False,
    )

    assert tagger2 is tagger


@pytest.mark.slow
def test_snakemake_execute():

    config_filename = aj("./tests/test_data/test_config.yml")

    cfg: Config = load_typed_config(config_name=config_filename)

    snakefile = jj('workflow', 'Snakefile')

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

    for filename in TEST_PROTOCOLS:

        document_name: str = strip_path_and_extension(filename)
        target_dir: str = jj(cfg.annotated_folder, filename.split('-')[1])

        assert isfile(jj(target_dir, f"{document_name}.zip"))


@pytest.mark.slow
def test_snakemake_word_frequency():

    workdir = aj("./tests/output/work_folder")
    config_filename = aj("./tests/test_data/test_config_output.yml")

    rmtree(workdir, ignore_errors=True)
    makedirs(workdir, exist_ok=True)
    makedirs(jj(workdir, "logs"), exist_ok=True)

    setup_parla_clarin_repository(TEST_PROTOCOLS, workdir, "riksdagen-corpus")
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
