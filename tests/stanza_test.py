import os
from typing import Any, Callable, Dict, List
from unittest.mock import Mock

import pytest
import untangle
from pytest import fixture
from workflow import annotate
from workflow.annotate.interface import TaggedDocument
from workflow.model.convert import dedent, pretokenize
from workflow.model.entities import Protocol

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
    {
        'speech_id': 'i-1',
        'speaker': 'A',
        'speech_date': '1958',
        'speech_index': 1,
        'document_name': 'prot-1958-fake@1',
        'text': 'Hej! Detta är en mening.\nJag heter Ove.\nVad heter du?',
        'annotation': 'token\tlemma\tpos\txpos\nHej\thej\tIN\tIN\n!\t!\tMID\tMID\nDetta\tdetta\tPN\tPN.NEU.SIN.DEF.SUB+OBJ\när\tvara\tVB\tVB.PRS.AKT\nen\ten\tDT\tDT.UTR.SIN.IND\nmening\tmening\tNN\tNN.UTR.SIN.IND.NOM\n.\t.\tMID\tMID\nJag\tjag\tPN\tPN.UTR.SIN.DEF.SUB\nheter\theta\tVB\tVB.PRS.AKT\nOve\tOve\tPM\tPM.NOM\n.\t.\tMID\tMID\nVad\tvad\tHP\tHP.NEU.SIN.IND\nheter\theta\tVB\tVB.PRS.AKT\ndu\tdu\tPN\tPN.UTR.SIN.DEF.SUB\n?\t?\tMAD\tMAD',
        'num_tokens': 15,
        'num_words': 15,
    },
    {
        'speech_id': 'i-3',
        'speaker': 'B',
        'speech_date': '1958',
        'speech_index': 2,
        'document_name': 'prot-1958-fake@2',
        'text': 'Jag heter Adam.\nOve är dum.',
        'annotation': 'token\tlemma\tpos\txpos\nJag\tjag\tPN\tPN.UTR.SIN.DEF.SUB\nheter\theta\tVB\tVB.PRS.AKT\nAdam\tAdam\tPM\tPM.NOM\n.\t.\tMID\tMID\nOve\tOve\tPM\tPM.NOM\när\tvara\tVB\tVB.PRS.AKT\ndum\tdum\tJJ\tJJ.POS.UTR.SIN.IND.NOM\n.\t.\tMAD\tMAD',
        'num_tokens': 8,
        'num_words': 8,
    },
]

EXPECTED_TAGGED_RESULT_FAKE_1960 = [
    {
        'speech_id': 'i-1',
        'speaker': 'A',
        'speech_date': '1960',
        'speech_index': 1,
        'document_name': 'prot-1960-fake@1',
        'text': 'Herr Talman! Jag talar.\nDet regnar ute.\nVisste du det?',
        'annotation': 'token\tlemma\tpos\txpos\nHerr\therr\tNN\tNN.UTR.SIN.IND.NOM\nTalman\tTalman\tPM\tPM.NOM\n!\t!\tMID\tMID\nJag\tjag\tPN\tPN.UTR.SIN.DEF.SUB\ntalar\ttala\tVB\tVB.PRS.AKT\n.\t.\tMID\tMID\nDet\tdet\tPN\tPN.NEU.SIN.DEF.SUB+OBJ\nregnar\tregna\tVB\tVB.PRS.AKT\nute\tute\tAB\tAB\n.\t.\tMID\tMID\nVisste\tveta\tVB\tVB.PRT.AKT\ndu\tdu\tPN\tPN.UTR.SIN.DEF.SUB\ndet\tdet\tPN\tPN.NEU.SIN.DEF.SUB+OBJ\n?\t?\tMAD\tMAD',
        'num_tokens': 14,
        'num_words': 14,
    },
    {
        'speech_id': 'i-3',
        'speaker': 'B',
        'speech_date': '1960',
        'speech_index': 2,
        'document_name': 'prot-1960-fake@2',
        'text': 'Jag håller med.\nTalmannen är snäll.',
        'annotation': 'token\tlemma\tpos\txpos\nJag\tjag\tPN\tPN.UTR.SIN.DEF.SUB\nhåller\thålla\tVB\tVB.PRS.AKT\nmed\tmed\tPL\tPL\n.\t.\tMID\tMID\nTalmannen\ttalman\tNN\tNN.UTR.SIN.DEF.NOM\när\tvara\tVB\tVB.PRS.AKT\nsnäll\tsnäll\tJJ\tJJ.POS.UTR.SIN.IND.NOM\n.\t.\tMAD\tMAD',
        'num_tokens': 8,
        'num_words': 8,
    },
    {
        'speech_id': 'i-4',
        'speaker': 'C',
        'speech_date': '1960',
        'speech_index': 3,
        'document_name': 'prot-1960-fake@3',
        'text': 'Jag håller också med.',
        'annotation': 'token\tlemma\tpos\txpos\nJag\tjag\tPN\tPN.UTR.SIN.DEF.SUB\nhåller\thålla\tVB\tVB.PRS.AKT\nockså\tockså\tAB\tAB\nmed\tmed\tPL\tPL\n.\t.\tMAD\tMAD',
        'num_tokens': 5,
        'num_words': 5,
    },
]


def test_stanza_tag_protocol(tagger: annotate.StanzaTagger):

    protocol: Protocol = Protocol(jj("tests", "test_data", "fake", "prot-1958-fake.xml"))

    result: List[Dict[str, Any]] = annotate.tag_speech_items(tagger, protocol.to_dict(), preprocess=True)

    assert result is not None
    assert len(result) == len(EXPECTED_TAGGED_RESULT_FAKE_1958)
    assert result == EXPECTED_TAGGED_RESULT_FAKE_1958


# @pytest.mark.skip(reason="deprecated")
# def test_stanza_bulk_tag_protocols(tagger: annotate.StanzaTagger):

#     protocols: List[Protocol] = [
#         Protocol(jj("tests", "test_data", "fake", "prot-1958-fake.xml")),
#         Protocol(jj("tests", "test_data", "fake", "prot-1960-fake.xml")),
#         Protocol(jj("tests", "test_data", "fake", "prot-1980-fake-empty.xml")),
#     ]

#     results: List[List[Dict[str, Any]]] = annotate.bulk_tag_protocols(tagger, protocols)

#     assert results is not None
#     assert len(results) == len(protocols)

#     assert results == [EXPECTED_TAGGED_RESULT_FAKE_1958, EXPECTED_TAGGED_RESULT_FAKE_1960, []]


def test_stanza_tag_protocol_with_no_speeches(tagger: annotate.StanzaTagger):

    file_data: untangle.Element = untangle.parse(jj("tests", "test_data", "fake", "prot-1980-fake-empty.xml"))
    protocol: Protocol = Protocol(file_data)

    result = annotate.tag_speech_items(tagger, protocol.to_dict())

    assert result is not None
    assert len(result) == 0


def test_stanza_tag_protocol_xml(tagger: annotate.StanzaTagger):

    # tagger = Mock(spec=annotate.StanzaTagger, tag=lambda *_, **_: [])

    input_filename: str = jj("tests", "test_data", "fake", "prot-1958-fake.xml")
    output_filename: str = jj("tests", "output", "prot-1958-fake.zip")

    annotate.tag_protocol_xml(input_filename, output_filename, tagger)

    assert os.path.isfile(output_filename)
