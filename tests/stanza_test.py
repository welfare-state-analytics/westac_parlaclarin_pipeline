import os
from typing import Callable, List

import pytest
import untangle
from pytest import fixture
from workflow import annotate
from workflow.annotate.interface import TaggedDocument
from workflow.model import Protocol, parse
from workflow.model.convert import dedent, pretokenize

nj = os.path.normpath
jj = os.path.join

MODEL_ROOT = "/data/sparv/models/stanza"

os.makedirs(jj("tests", "output"), exist_ok=True)

# pylint: disable=redefined-outer-name
if not os.path.isdir(MODEL_ROOT):
    pytest.skip(f"Skipping Stanza tests since model path {MODEL_ROOT} doesn't exist.", allow_module_level=True)


def dehyphen(text: str) -> str:
    return text


@fixture(scope="session")
def tagger() -> annotate.StanzaTagger:
    preprocessors: List[Callable[[str], str]] = [dedent, dehyphen, str.strip, pretokenize]
    _tagger: annotate.StanzaTagger = annotate.StanzaTagger(model_root=MODEL_ROOT, preprocessors=preprocessors)
    return _tagger


def test_stanza_annotator_to_document(tagger: annotate.StanzaTagger):
    text: str = "Detta är ett test!"

    tagged_documents: List[TaggedDocument] = tagger.tag(text, preprocess=True)

    assert len(tagged_documents) == 1

    assert tagged_documents[0]['token'] == ['Detta', 'är', 'ett', 'test', '!']
    assert tagged_documents[0]['lemma'] == ['detta', 'vara', 'en', 'test', '!']
    assert tagged_documents[0]['pos'] == ['PN', 'VB', 'DT', 'NN', 'MAD']


def test_stanza_tag(tagger: annotate.StanzaTagger):
    text: str = "Hej! Detta är ett test!"

    tagged_documents: List[TaggedDocument] = tagger.tag(text, preprocess=True)

    assert tagged_documents == [
        {
            'lemma': ['hej', '!', 'detta', 'vara', 'en', 'test', '!'],
            'num_tokens': 7,
            'num_words': 7,
            'pos': ['IN', 'MID', 'PN', 'VB', 'DT', 'NN', 'MAD'],
            'token': ['Hej', '!', 'Detta', 'är', 'ett', 'test', '!'],
            'xpos': [
                'IN',
                'MID',
                'PN.NEU.SIN.DEF.SUB+OBJ',
                'VB.PRS.AKT',
                'DT.NEU.SIN.IND',
                'NN.NEU.SIN.IND.NOM',
                'MAD',
            ],
        }
    ]


EXPECTED_TAGGED_RESULT_FAKE_1958 = [
    'token\tlemma\tpos\txpos\nHej\thej\tIN\tIN\n!\t!\tMID\tMID\nDetta\tdetta\tPN\tPN.NEU.SIN.DEF.SUB+OBJ\när\tvara\tVB\tVB.PRS.AKT\nen\ten\tDT\tDT.UTR.SIN.IND\nmening\tmening\tNN\tNN.UTR.SIN.IND.NOM\n.\t.\tMAD\tMAD',
    'token\tlemma\tpos\txpos\nJag\tjag\tPN\tPN.UTR.SIN.DEF.SUB\nheter\theta\tVB\tVB.PRS.AKT\nOve\tOve\tPM\tPM.NOM\n.\t.\tMID\tMID\nVad\tvad\tHP\tHP.NEU.SIN.IND\nheter\theta\tVB\tVB.PRS.AKT\ndu\tdu\tPN\tPN.UTR.SIN.DEF.SUB\n?\t?\tMAD\tMAD',
    'token\tlemma\tpos\txpos\nJag\tjag\tPN\tPN.UTR.SIN.DEF.SUB\nheter\theta\tVB\tVB.PRS.AKT\nAdam\tAdam\tPM\tPM.NOM\n.\t.\tMAD\tMAD',
    'token\tlemma\tpos\txpos\nOve\tOve\tPM\tPM.NOM\när\tvara\tVB\tVB.PRS.AKT\ndum\tdum\tJJ\tJJ.POS.UTR.SIN.IND.NOM\n.\t.\tMAD\tMAD',
]


def test_stanza_tag_protocol(tagger: annotate.StanzaTagger):

    protocol: Protocol = parse.ProtocolMapper.to_protocol(jj("tests", "test_data", "fake", "prot-1958-fake.xml"))

    annotate.tag_protocol(tagger, protocol, preprocess=True)

    assert [u.annotation for u in protocol.utterances] == EXPECTED_TAGGED_RESULT_FAKE_1958


def test_stanza_tag_protocol_with_no_utterances(tagger: annotate.StanzaTagger):

    file_data: untangle.Element = untangle.parse(jj("tests", "test_data", "fake", "prot-1980-fake-empty.xml"))
    protocol: Protocol = parse.ProtocolMapper.to_protocol(file_data)

    protocol = annotate.tag_protocol(tagger, protocol)

    assert protocol is not None


def test_stanza_tag_protocol_xml(tagger: annotate.StanzaTagger):

    # tagger = Mock(spec=annotate.StanzaTagger, tag=lambda *_, **_: [])

    input_filename: str = jj("tests", "test_data", "fake", "prot-1958-fake.xml")
    output_filename: str = jj("tests", "output", "prot-1958-fake.zip")

    annotate.tag_protocol_xml(input_filename, output_filename, tagger)

    assert os.path.isfile(output_filename)
