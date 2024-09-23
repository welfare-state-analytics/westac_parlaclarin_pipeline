import os
import shutil
import uuid

from pyriksprot_tagger.utility import expand_basenames, expand_target_files

TEST_BASENAMES = [
    'prot-198687--11',
    'prot-200405--7',
    'prot-1961--fk--6',
    'prot-1961--ak--5',
    'prot-1936--ak--8',
]


def _setup_test_files(folder: str):
    shutil.rmtree(folder, ignore_errors=True)
    os.makedirs(folder, exist_ok=True)
    for basename in TEST_BASENAMES:
        target_folder: str = f'{folder}/{basename.split("-")[1]}'
        os.makedirs(target_folder, exist_ok=True)
        with open(os.path.join(target_folder, f"{basename}.xml"), 'w', encoding='utf8') as f:
            f.write('')


def test_expand_basenames():
    folder: str = f'tests/output/{str(uuid.uuid4())[:8]}'
    shutil.rmtree(folder, ignore_errors=True)
    _setup_test_files(folder)
    years, filenames = expand_basenames('tests/output/work_folder/riksdagen-records/data', 'xml')
    assert years == ['198687', '200405', '1961', '1961', '1936']
    assert filenames == TEST_BASENAMES
    shutil.rmtree(folder, ignore_errors=True)


def test_expand_target_files():
    folder: str = f'tests/output/{str(uuid.uuid4())[:8]}'
    shutil.rmtree(folder, ignore_errors=True)
    _setup_test_files(folder)

    source_folder = folder
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
    shutil.rmtree(folder, ignore_errors=True)
