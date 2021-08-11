import os
from os.path import join as jj
from os.path import normpath as nj

import pytest
import snakemake
from snakemake.io import expand, glob_wildcards

from .utility import create_data_testbench


def test_expand_call_arguments():
    target_folder = nj("/data/riksdagen_corpus_data/riksdagen-corpus-exports/speech_xml")
    source_folder = nj("/data/riksdagen_corpus_data/riksdagen-corpus/corpus/")
    extension = "xml"
    years, basenames = glob_wildcards(jj(source_folder, "{year}", f"{{file}}.{extension}"))

    filenames = expand(jj(target_folder, '{year}', f'{{basename}}.{extension}'), zip, year=years, basename=basenames)

    assert len(filenames) == len(years)

@pytest.mark.skip("long running")
@pytest.mark.long_running
def test_create_data_testbench():

    root_path: str = nj("tests/test_data/work_folder")
    repository_name: str = "riksdagen-corpus"

    create_data_testbench(root_path=root_path, repository_name=repository_name)
    # run test: snakemake -j1 --config config_filename=test_config.yaml

    # status = snakemake.snakemake(
    #     snakefile='./workflow/Snakefile',
    #     cores=1,
    #     config={'config_filename': 'test_config.yml'},
    #     unlock=True,
    # )


STANZA_MODELS_FOLDER = "./tests/test_data/work_folder/sparv/models/stanza"


@pytest.mark.skipif(not os.path.isdir(STANZA_MODELS_FOLDER), reason=f"Stanza models not found in {STANZA_MODELS_FOLDER}")
def test_snakemake_execute():

    snakefile = jj('workflow', 'Snakefile')
    snakemake_args = {"workdir": "."}

    config = dict(config_filename="./tests/test_data/test_config.yml")
    success = snakemake.snakemake(
        snakefile, config=config, debug=True, **snakemake_args, keep_target_files=True, cores=1
    )

    assert success
