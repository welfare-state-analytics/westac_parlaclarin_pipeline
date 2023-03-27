import glob
from os import environ, makedirs
from os.path import abspath as aj
from os.path import isfile
from os.path import join as jj
from os.path import normpath as nj
from shutil import rmtree
from typing import List

import pytest
import snakemake
from snakemake.io import expand, glob_wildcards

from workflow.config import Config
from workflow.utility import strip_path_and_extension

from .utility import (
    RIKSPROT_SAMPLE_DATA_FOLDER,
    create_sample_xml_repository,
    setup_work_folder_for_tagging_with_stanza,
)


@pytest.mark.skipif(environ.get("RIKSPROT_DATA_FOLDER") is None, reason="no data")
def test_expand_call_arguments():

    source_folder = jj(environ["RIKSPROT_DATA_FOLDER"], "riksdagen-corpus/corpus/protocols")
    target_folder = nj("/data/westac/riksdagen_corpus_data/riksdagen-corpus-exports/speech_xml")
    extension = "xml"
    years, basenames = glob_wildcards(jj(source_folder, "{year}", f"{{file}}.{extension}"))

    filenames = expand(jj(target_folder, '{year}', f'{{basename}}.{extension}'), zip, year=years, basename=basenames)

    assert len(filenames) == len(years)


@pytest.mark.slow
def test_snakemake_execute():

    config_filename = aj("./tests/test_data/test_config.yml")

    cfg: Config = Config.load(source=config_filename)

    snakefile = jj('workflow', 'Snakefile')

    rmtree(cfg.tagged_frames_folder, ignore_errors=True)
    makedirs(cfg.tagged_frames_folder, exist_ok=True)

    success = snakemake.snakemake(
        snakefile,
        config=dict(config_filename=config_filename),
        # debug=True,
        # workdir=workdir,
        keep_target_files=True,
        cores=4,
        verbose=True,
    )

    assert success

    source_files: List[str] = glob.glob(
        jj(cfg.data_folder, 'riksdagen-corpus/corpus/protocols/**/prot*.xml'), recursive=True
    )

    for filename in source_files:

        document_name: str = strip_path_and_extension(filename)
        target_dir: str = jj(cfg.tagged_frames_folder, document_name.split('-')[1])

        assert isfile(jj(target_dir, f"{document_name}.zip"))


@pytest.mark.slow
def test_snakemake_word_frequency():

    protocols: List[str] = [
        'prot-1936--ak--8.xml',
        'prot-197778--160.xml',
    ]

    workdir = aj(RIKSPROT_SAMPLE_DATA_FOLDER)
    config_filename = aj("./tests/test_data/test_config.yml")

    rmtree(workdir, ignore_errors=True)
    makedirs(workdir, exist_ok=True)
    makedirs(jj(workdir, "logs"), exist_ok=True)

    create_sample_xml_repository(protocols=protocols, root_path=workdir, tag="main")
    setup_work_folder_for_tagging_with_stanza(workdir)

    snakefile = jj('workflow', 'Snakefile')

    snakemake.snakemake(
        snakefile,
        config=dict(config_filename=config_filename, processes=4),
        # debug=True,
        # workdir=workdir,
        keep_target_files=True,
        cores=2,
        verbose=True,
        targets=['word_frequency'],
    )

    assert isfile(jj(workdir, "riksdagen-corpus-term-frequencies.pkl"))
