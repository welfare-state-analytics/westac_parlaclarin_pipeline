from os.path import join as jj
from os.path import normpath as nj

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


def test_snakemake_execute():
    snakefile = jj('workflow', 'Snakefile')
    snakemake_args = {"workdir": "."}

    # logger.log_handler = []
    # progress = log_handler.LogHandler(progressbar=not simple_target, log_level=log_level, log_file_level=log_file_level)
    # snakemake_args["log_handler"] = [progress.log_handler]

    # config["log_server"] = progress.log_server
    config = dict()
    success = snakemake.snakemake(
        snakefile,
        config=config,
        debug=True,
        **snakemake_args,
        keep_target_files=True,
        cores=1,
    )

    assert success
