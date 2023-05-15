from pyriksprot_tagger.utility import expand_basenames


def test_expand_basenames():
    years, filenames = expand_basenames('tests/output/work_folder/riksdagen-corpus/corpus/protocols', 'xml')
    assert years == ['198687', '200405', '1961', '1961', '1936']
    assert filenames == [
        'prot-198687--11',
        'prot-200405--7',
        'prot-1961--fk--6',
        'prot-1961--ak--5',
        'prot-1936--ak--8',
    ]


# def test_expand_target_files():
#     assert expand_target_files(
#         'tests/output/work_folder/riksdagen-corpus/corpus/protocols',
#         'xml',
#         ['198687', '200405', '1961', '1961', '1936'],
#     ) == ['tests/output/work_folder/riksdagen-corpus/corpus/protocols/198687/prot-198687--11.xml']
