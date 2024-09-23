import os
from os.path import abspath as aj
from os.path import join as jj

import pyriksprot
import snakemake
from pyriksprot import ITaggerFactory, TaggerRegistry
from pyriksprot.configuration import Config
from pyriksprot_tagger.taggers import StanzaTaggerFactory

# from utility import setup_working_folder  # pylint: disable=import-error


def run_snakemake():
    # test_protocols: List[str] = [
    #     'prot-1936--ak--8.xml',
    #     # 'prot-1961--ak--5.xml',
    #     # 'prot-1961--fk--6.xml',
    #     # 'prot-198687--11.xml',
    #     # 'prot-200405--7.xml',
    #     # 'prot-197778--160.xml',
    # ]

    # rmtree(workdir, ignore_errors=True)
    # setup_working_folder(root_path=workdir, test_protocols=test_protocols)

    snakemake.snakemake(
        jj('pyriksprot_tagger', 'workflow', 'Snakefile'),
        config=dict(config_filename=aj("./tests/test_data/test_config.yml")),
        debug=True,
        keep_target_files=True,
        cores=1,
        max_threads=1,
        verbose=True,
        assume_shared_fs=False,
    )


def run_tag_protocol_xml():
    config_filename: str = aj("./tests/test_data/test_config.yml")
    cfg: Config = Config.load(source=config_filename)

    factory: ITaggerFactory = StanzaTaggerFactory.factory(
        stanza_datadir=cfg.get("tagger:stanza_datadir"),
        dehyphen_datadir=cfg.get("dehyphen:folder"),
        word_frequencies=cfg.get("dehyphen:tf_filename"),
        use_gpu=False,
    )
    tagger: pyriksprot.ITagger = TaggerRegistry.get(factory=factory)

    input_filename: str = jj("tests", "test_data", "fake", "prot-1958-fake.xml")
    output_filename: str = jj("tests", "output", "prot-1958-fake.zip")

    pyriksprot.tag_protocol_xml(
        input_filename,
        output_filename,
        tagger,
        storage_format="json",
    )

    assert os.path.isfile(output_filename)


# run_tag_protocol_xml()
run_snakemake()
