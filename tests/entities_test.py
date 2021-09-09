import os

import pytest
import untangle
from workflow.model import entities as model
from workflow.model.utility import hasattr_path

jj = os.path.join


@pytest.mark.parametrize(
    'filename, expected_speech_count, expected_non_empty_speech_count',
    [("prot-1933--fk--5.xml", 1, 1), ("prot-1955--ak--22.xml", 82, 79), ('prot-199192--127.xml', 206, 206)],
)
def test_parse_correct_xml(filename, expected_speech_count, expected_non_empty_speech_count):

    data = untangle.parse(jj("tests", "test_data", "source", filename))
    has_utterances = hasattr_path(data, 'teiCorpus.TEI.text.body.div.u')

    assert hasattr_path(data, "teiCorpus.teiHeader.fileDesc.titleStmt.title")
    assert hasattr_path(data, "teiCorpus.TEI.teiHeader.fileDesc.titleStmt.title")
    assert hasattr_path(data, "teiCorpus.TEI.text.front.div.docDate")
    assert hasattr_path(data, "teiCorpus.TEI.text.body.div.u") == has_utterances, "No u-tags in XML"

    protocol = model.Protocol(data, remove_empty=False)
    assert len(protocol.speeches) == expected_speech_count, "speech length"

    protocol = model.Protocol(data, remove_empty=True)
    assert len(protocol.speeches) == expected_non_empty_speech_count

    assert all(x.text != "" for x in protocol.speeches)
    assert os.path.splitext(filename)[0] == protocol.name
    assert protocol.date is not None
    assert protocol.has_speech_text() == any(x.text != "" for x in protocol.speeches)

    dict_protocols = protocol.to_dict(skip_size=3)
    assert len(dict_protocols) == len(protocol.speeches)
    assert all(len(x['text']) > 3 for x in dict_protocols)

    dict_protocols = protocol.to_dict(skip_size=100)
    assert all(len(x['text']) > 100 for x in dict_protocols)


@pytest.mark.parametrize(
    'filename',
    [
        ("prot-197879--14.xml"),
        ("prot-199596--35.xml"),
    ],
)
def test_parse_xml_with_no_utterances(filename):

    protocol = model.Protocol(jj("tests", "test_data", "source", filename), remove_empty=False)

    assert len(protocol.speeches) == 0, "speech empty"
    assert not protocol.has_speech_text()


@pytest.mark.parametrize(
    'filename, expected_speech_count',
    [
        ('prot-199192--21.xml', 0),
    ],
)
def test_parse_xml_with_faulty_prev_attribute(filename, expected_speech_count):

    data = untangle.parse(jj("tests", "test_data", "source", filename))

    protocol = model.Protocol(data, remove_empty=False)
    assert len(protocol.speeches) != expected_speech_count, "speech length"
