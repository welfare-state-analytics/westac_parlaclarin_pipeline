from os.path import join as jj
from typing import List

from workflow.model.utility import ensure_path, touch, unlink
from workflow.utility import expand_basenames, expand_target_files

TEST_DUMMY_FILENAMES = [
    'prot-200708--13',
    'prot-200001--37',
    'prot-198485--141',
    'prot-197576--121',
    'prot-199697--42',
    'prot-1944-höst-fk--28',
    'prot-200607--73',
    'prot-200304--74',
    'prot-1952--fk--22',
    'prot-1932--fk--38',
]


def create_test_source_tree(corpus_path: str, filenames: List[str]):
    unlink(corpus_path)
    filenames = [
        'prot-200708--13',
        'prot-200001--37',
        'prot-198485--141',
        'prot-197576--121',
        'prot-199697--42',
        'prot-1944-höst-fk--28',
        'prot-200607--73',
        'prot-200304--74',
        'prot-1952--fk--22',
        'prot-1932--fk--38',
    ]
    for filename in filenames:
        year_folder = jj(corpus_path, filename.split('-')[1])
        target_file = jj(year_folder, f"{filename}.xml")
        ensure_path(target_file)
        touch(target_file)


def test_expand_basenames():

    source_folder: str = jj("tests", "output", "corpus")
    create_test_source_tree(source_folder, TEST_DUMMY_FILENAMES)

    source_years, target_basenames = expand_basenames(source_folder, "xml")

    assert set(target_basenames) == set(TEST_DUMMY_FILENAMES)
    assert set(source_years) == {filename.split('-')[1] for filename in TEST_DUMMY_FILENAMES}

    source_years, target_basenames = expand_basenames(source_folder, "xml", years=197576)

    assert set(target_basenames) == {'prot-197576--121'}
    assert set(source_years) == {'197576'}

    source_years, target_basenames = expand_basenames(source_folder, "xml", years=1975)

    assert set(target_basenames) == {'prot-197576--121'}
    assert set(source_years) == {'197576'}

    source_years, target_basenames = expand_basenames(source_folder, "xml", years=[1975, 2000])

    assert set(target_basenames) == {'prot-197576--121', 'prot-200001--37'}
    assert set(source_years) == {'197576', '200001'}


def test_expand_target_files():

    source_folder: str = jj("tests", "output", "corpus")
    target_folder: str = jj("tests", "output", "annotated")

    create_test_source_tree(source_folder, TEST_DUMMY_FILENAMES)

    target_files = expand_target_files(source_folder, "xml", target_folder, "zip")

    assert set(target_files) == {
        jj("tests", "output", "annotated", filename.split('-')[1], f"{filename}.zip")
        for filename in TEST_DUMMY_FILENAMES
    }


# def test_resolve_input_arguments():
#     source_folder: str = jj("tests", "output", "corpus")

#     create_test_source_tree(source_folder, TEST_DUMMY_FILENAMES)

#     config_filename: str = "config.yml"
#     typed_config: Config = load_typed_config(config_filename)

#     source_folder = typed_config.parla_clarin.folder
#     source_extension = "xml"

#     target_folder = typed_config.annotated_folder
#     target_extension = "zip"

#     source_years, target_basenames = glob_wildcards(jj(source_folder, r"{year,\d+}", f"{{file}}.{source_extension}"))
#     source_years, target_basenames = expand_basenames(source_folder, source_extension)

#     target_files = expand(
#         jj(target_folder, "{year}", f"{{basename}}.{target_extension}"),
#         zip,
#         year=source_years,
#         basename=target_basenames,
#     )

#     assert target_files is not None
