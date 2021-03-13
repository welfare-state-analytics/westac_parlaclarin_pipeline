import os

from snakemake.io import expand, glob_wildcards

from .utility import create_data_testbench

# directories, files = glob_wildcards("data01/{dir}/{file}")

# rule all:
#     input:
#         expand("data01/temp/{dir}/{file}.moved.Stp",
#                zip, dir=directories, file=files)

# rule copy:
#     input:
#         "data01/{dir}/{file}.Stp"
#     output:
#         "data01/temp/{dir}/{file}.moved.Stp"
#     shell:
#         "cp {input} {output}"


def test_expand_call_arguments():
    target_folder = "/data/riksdagen_corpus_data/riksdagen-corpus-exports/speech_xml"
    source_folder = "/data/riksdagen_corpus_data/riksdagen-corpus/corpus/"
    extension = "xml"
    years, basenames = glob_wildcards(os.path.join(source_folder, f"{{year}}/{{file}}.{extension}"))

    filenames = expand(f'{target_folder}/{{year}}/{{basename}}.{extension}', zip, year=years, basename=basenames)

    assert len(filenames) == len(years)


def test_snakemake_rules():

    root_path: str = "tests/test_data/work_folder"
    repository_name: str = "riksdagen-corpus"

    create_data_testbench(root_path=root_path, repository_name=repository_name)
