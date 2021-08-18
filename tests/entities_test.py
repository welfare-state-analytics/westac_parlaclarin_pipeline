import os

import pytest
import untangle
from workflow.model import entities as model
from workflow.model.utility import hasattr_path

jj = os.path.join


@pytest.mark.parametrize(
    'filename',
    [
        ("prot-1933--fk--5.xml"),
        ("prot-1955--ak--22.xml"),
        ("prot-197879--14.xml"),
        ("prot-199596--35.xml"),
    ],
)
def test_parse_xml(filename):

    data = untangle.parse(jj("tests", "test_data", "source", filename))
    has_utterances = hasattr_path(data, 'teiCorpus.TEI.text.body.div.u')

    assert hasattr_path(data, "teiCorpus.teiHeader.fileDesc.titleStmt.title")
    assert hasattr_path(data, "teiCorpus.TEI.teiHeader.fileDesc.titleStmt.title")
    assert hasattr_path(data, "teiCorpus.TEI.text.front.div.docDate")
    assert hasattr_path(data, "teiCorpus.TEI.text.body.div.u") == has_utterances, "No u-tags in XML"

    protocol = model.Protocol(data, remove_empty=False)
    expected_speech_count = (
        0 if not has_utterances else len([u for u in data.teiCorpus.TEI.text.body.div.u if u['prev'] is None])
    )
    assert len(protocol.speeches) == expected_speech_count, "speech length"

    empty_utterances = (
        []
        if not has_utterances
        else [
            u
            for u in data.teiCorpus.TEI.text.body.div.u
            if not hasattr_path(u, 'seg') and u['prev'] is None and u['next'] is None
        ]
    )
    protocol = model.Protocol(data, remove_empty=True)
    assert len(protocol.speeches) == expected_speech_count - len(empty_utterances)

    assert all(x.text != "" for x in protocol.speeches)
    assert os.path.splitext(filename)[0] == protocol.name
    assert protocol.date is not None
    assert protocol.has_speech_text() == any(x.text != "" for x in protocol.speeches)

    dict_protocols = protocol.to_dict(skip_size=3)
    assert len(dict_protocols) == len(protocol.speeches)
    assert all(len(x['text']) > 3 for x in dict_protocols)

    dict_protocols = protocol.to_dict(skip_size=100)
    assert all(len(x['text']) > 100 for x in dict_protocols)
