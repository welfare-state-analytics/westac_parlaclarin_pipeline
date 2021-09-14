import os
from os.path import abspath as aj
from os.path import join as jj
from shutil import rmtree
from typing import List

import pyriksprot
import pytest
import snakemake
from workflow.config.typed_config import Config, load_typed_config
from workflow.taggers import StanzaTagger, TaggerRegistry

from .utility import setup_working_folder

# from utility import setup_working_folder  # pylint: disable=import-error


@pytest.mark.skip(reason="Very slow")
@pytest.mark.slow
def run_snakemake():

    test_protocols: List[str] = [
        'prot-1936--ak--8.xml',
        'prot-1961--ak--5.xml',
        'prot-1961--fk--6.xml',
        'prot-198687--11.xml',
        'prot-200405--7.xml',
        'prot-197778--160.xml',
    ]

    workdir = aj("./tests/test_data/work_folder")

    rmtree(workdir, ignore_errors=True)
    setup_working_folder(root_path=workdir, test_protocols=test_protocols)

    snakemake.snakemake(
        jj('workflow', 'Snakefile'),
        config=dict(
            config_filename=aj("./tests/test_data/test_config.yml"),
        ),
        debug=True,
        keep_target_files=True,
        cores=1,
        verbose=True,
    )


@pytest.mark.skip(reason="Very slow")
@pytest.mark.slow
def run_tag_protocol_xml():

    config_filename: str = aj("./tests/test_data/test_config.yml")
    cfg: Config = load_typed_config(config_filename)

    tagger: pyriksprot.ITagger = TaggerRegistry.get(
        tagger_cls=StanzaTagger,
        model=cfg.stanza_dir,
        dehyphen_opts=dict(word_frequency_filename=cfg.word_frequency.fullname, **cfg.dehyphen.opts),
        use_gpu=False,
    )

    input_filename: str = jj("tests", "test_data", "fake", "prot-1958-fake.xml")
    output_filename: str = jj("tests", "output", "prot-1958-fake.zip")

    pyriksprot.tag_protocol_xml(
        input_filename,
        output_filename,
        tagger,
        storage_format="json",
    )

    assert os.path.isfile(output_filename)


run_tag_protocol_xml()
