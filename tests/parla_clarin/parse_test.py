import os
import sys

sys.path.append((lambda d: os.path.join(os.getcwd().split(d)[0], d))("parla_clarin_pipeline"))

import untangle
from workflow.model import entities as model
from workflow.model.utility import hasattr_path


def test_parse_xml():

    data = untangle.parse("tests/test_data/test.xml")

    assert hasattr_path(data, "teiCorpus.TEI.text.body.div.u"), "No u-tags in XML"

    div = data.teiCorpus.TEI.text.body.div
    assert len(div.u) == 8, "Wrong length"

    assert [div.u[i]["xml:id"] for i in range(0, 8)] == [f"i-{i+1}" for i in range(0, 8)]


def test_parse_parla_clarin_xml_when_valid_xml_has_expected_content():

    data = untangle.parse("tests/test_data/test.xml")

    protocol = model.Protocol(data)

    assert len(protocol.speeches) == 4
    assert [len(s.paragraphs) for s in protocol.speeches] == [4, 8, 3, 6]
    assert protocol.name == "test"
    assert protocol.date == "1958-01-01"

    expected_utterances = [
        ["a b c d", "e?\nf g h i.\nj k l m"],
        ["a\nf g h i.\nj k l m", "e?\nf g h i.\nj k l m", "n\no p."],
        ["a b\nf g h i.\nj k l m o"],
        ["a c\nf g h i.\nj k l m", "a\nf g h i.\nj k l m"],
    ]
    assert expected_utterances == [s.utterances for s in protocol.speeches]

    expected_utterances_segments = [
        [["a b c d"], ["e?", "f g h i.", "j k l m"]],
        [["a", "f g h i.", "j k l m"], ["e?", "f g h i.", "j k l m"], ["n", "o p."]],
        [["a b", "f g h i.", "j k l m o"]],
        [["a c", "f g h i.", "j k l m"], ["a", "f g h i.", "j k l m"]],
    ]
    assert expected_utterances_segments == [s.utterances_segments for s in protocol.speeches]

    assert [s.speech_id for s in protocol.speeches] == ["i-1", "i-3", "i-6", "i-7"]
    assert [s.speaker for s in protocol.speeches] == ["A", "B", "C", "D"]

def test_protocol():

    data = untangle.parse("tests/test_data/prot-199293--72.xml")

    protocol = model.Protocol(data)

    utterances = protocol.data.teiCorpus.TEI.text.body.div.u

    assert len(utterances) == 205

    assert len(protocol.speeches) == len(utterances) - len([ u for u in utterances if u['prev'] == 'cont'])

    assert protocol is not None
