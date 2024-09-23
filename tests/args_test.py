import tempfile
from os.path import join as jj
from typing import List

from pyriksprot.utility import ensure_path, touch, unlink
from pyriksprot_tagger.utility import expand_basenames, expand_target_files

TEST_DUMMY_FILENAMES = [
    'prot-200708--013',
    'prot-200001--037',
    'prot-198485--141',
    'prot-197576--121',
    'prot-199697--042',
    'prot-1944-höst-fk--028',
    'prot-200607--073',
    'prot-200304--074',
    'prot-1952--fk--022',
    'prot-1932--fk--038',
]


def create_test_source_tree(corpus_path: str, filenames: List[str]):
    unlink(corpus_path)
    for filename in filenames:
        year_folder = jj(corpus_path, filename.split('-')[1])
        target_file = jj(year_folder, f"{filename}.xml")
        ensure_path(target_file)
        touch(target_file)


def test_expand_basenames():
    with tempfile.TemporaryDirectory() as temp_folder:
        source_folder: str = jj(temp_folder, "corpus")
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

        assert set(target_basenames) == {'prot-197576--121', 'prot-200001--037'}
        assert set(source_years) == {'197576', '200001'}


def test_expand_target_files():
    with tempfile.TemporaryDirectory() as temp_folder:
        source_folder: str = jj(temp_folder, "corpus")
        target_folder: str = jj(temp_folder, "annotated")

        create_test_source_tree(source_folder, TEST_DUMMY_FILENAMES)

        target_files = expand_target_files(source_folder, "xml", target_folder, "zip")

        assert set(target_files) == {
            jj(temp_folder, "annotated", filename.split('-')[1], f"{filename}.zip") for filename in TEST_DUMMY_FILENAMES
        }
