from pyriksprot_tagger.utility import expand_basenames, expand_target_files

TEST_BASENAMES = [
    'prot-198687--11',
    'prot-200405--7',
    'prot-1961--fk--6',
    'prot-1961--ak--5',
    'prot-1936--ak--8',
]


def test_expand_basenames():
    years, filenames = expand_basenames('tests/output/work_folder/riksdagen-corpus/corpus/protocols', 'xml')
    assert years == ['198687', '200405', '1961', '1961', '1936']
    assert filenames == TEST_BASENAMES


def test_expand_target_files():

    source_folder = 'tests/output/work_folder/riksdagen-corpus/corpus/protocols'
    source_extension = 'xml'

    target_folder: str = 'tests/output'
    target_extension = 'zip'

    target_files: list[str] = expand_target_files(
        source_folder=source_folder,
        source_extension=source_extension,
        target_folder=target_folder,
        target_extension=target_extension,
        years=None,
    )

    assert target_files is not None

    assert target_files == [f'tests/output/{x.split("-")[1]}/{x}.zip' for x in TEST_BASENAMES]
