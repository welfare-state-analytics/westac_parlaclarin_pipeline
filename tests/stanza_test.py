import os
from typing import Callable, List

import pytest
import untangle
from pytest import fixture
from workflow import annotate
from workflow.annotate.interface import TaggedDocument
from workflow.model import Protocol, Speech, parse
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
    'token\tlemma\tpos\txpos\nHej\thej\tIN\tIN\n!\t!\tMID\tMID\nDetta\tdetta\tPN\tPN.NEU.SIN.DEF.SUB+OBJ\när\tvara\tVB\tVB.PRS.AKT\nen\ten\tDT\tDT.UTR.SIN.IND\nmening\tmening\tNN\tNN.UTR.SIN.IND.NOM\n.\t.\tMID\tMID\nJag\tjag\tPN\tPN.UTR.SIN.DEF.SUB\nheter\theta\tVB\tVB.PRS.AKT\nOve\tOve\tPM\tPM.NOM\n.\t.\tMID\tMID\nVad\tvad\tHP\tHP.NEU.SIN.IND\nheter\theta\tVB\tVB.PRS.AKT\ndu\tdu\tPN\tPN.UTR.SIN.DEF.SUB\n?\t?\tMAD\tMAD',
    'token\tlemma\tpos\txpos\nJag\tjag\tPN\tPN.UTR.SIN.DEF.SUB\nheter\theta\tVB\tVB.PRS.AKT\nAdam\tAdam\tPM\tPM.NOM\n.\t.\tMID\tMID\nOve\tOve\tPM\tPM.NOM\när\tvara\tVB\tVB.PRS.AKT\ndum\tdum\tJJ\tJJ.POS.UTR.SIN.IND.NOM\n.\t.\tMAD\tMAD',
]

EXPECTED_TAGGED_RESULT_FAKE_1960 = [
    'token\tlemma\tpos\txpos\nHerr\therr\tNN\tNN.UTR.SIN.IND.NOM\nTalman\tTalman\tPM\tPM.NOM\n!\t!\tMID\tMID\nJag\tjag\tPN\tPN.UTR.SIN.DEF.SUB\ntalar\ttala\tVB\tVB.PRS.AKT\n.\t.\tMID\tMID\nDet\tdet\tPN\tPN.NEU.SIN.DEF.SUB+OBJ\nregnar\tregna\tVB\tVB.PRS.AKT\nute\tute\tAB\tAB\n.\t.\tMID\tMID\nVisste\tveta\tVB\tVB.PRT.AKT\ndu\tdu\tPN\tPN.UTR.SIN.DEF.SUB\ndet\tdet\tPN\tPN.NEU.SIN.DEF.SUB+OBJ\n?\t?\tMAD\tMAD',
    'token\tlemma\tpos\txpos\nJag\tjag\tPN\tPN.UTR.SIN.DEF.SUB\nhåller\thålla\tVB\tVB.PRS.AKT\nmed\tmed\tPL\tPL\n.\t.\tMID\tMID\nTalmannen\ttalman\tNN\tNN.UTR.SIN.DEF.NOM\när\tvara\tVB\tVB.PRS.AKT\nsnäll\tsnäll\tJJ\tJJ.POS.UTR.SIN.IND.NOM\n.\t.\tMAD\tMAD',
    'token\tlemma\tpos\txpos\nJag\tjag\tPN\tPN.UTR.SIN.DEF.SUB\nhåller\thålla\tVB\tVB.PRS.AKT\nockså\tockså\tAB\tAB\nmed\tmed\tPL\tPL\n.\t.\tMAD\tMAD',
]


def test_stanza_tag_protocol(tagger: annotate.StanzaTagger):

    protocol: Protocol = parse.ProtocolMapper.to_protocol(jj("tests", "test_data", "fake", "prot-1958-fake.xml"))
    speeches: List[Speech] = protocol.to_speeches(merge_strategy='n')

    tagged_speeches: List[Speech] = annotate.tag_speeches(tagger, speeches, preprocess=True)

    assert tagged_speeches is not None
    assert len(tagged_speeches) == len(EXPECTED_TAGGED_RESULT_FAKE_1958)
    assert [s.annotation for s in tagged_speeches] == EXPECTED_TAGGED_RESULT_FAKE_1958


def test_stanza_tag_protocol_with_no_speeches(tagger: annotate.StanzaTagger):

    file_data: untangle.Element = untangle.parse(jj("tests", "test_data", "fake", "prot-1980-fake-empty.xml"))
    protocol: Protocol = parse.ProtocolMapper.to_protocol(file_data)
    speeches: List[Speech] = protocol.to_speeches(merge_strategy='n')

    tagged_speeches: List[Speech] = annotate.tag_speeches(tagger, speeches)

    assert tagged_speeches is not None
    assert len(tagged_speeches) == 0


def test_stanza_tag_protocol_xml(tagger: annotate.StanzaTagger):

    # tagger = Mock(spec=annotate.StanzaTagger, tag=lambda *_, **_: [])

    input_filename: str = jj("tests", "test_data", "fake", "prot-1958-fake.xml")
    output_filename: str = jj("tests", "output", "prot-1958-fake.zip")

    annotate.tag_protocol_xml(input_filename, output_filename, tagger)

    assert os.path.isfile(output_filename)
