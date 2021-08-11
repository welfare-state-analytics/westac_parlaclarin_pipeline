import os
from typing import Any, Callable, Dict, List
from uuid import uuid4

import stanza
import untangle
from pytest import fixture
from workflow import annotate
from workflow.model.convert import dedent, pretokenize
from workflow.model.entities import Protocol

nj = os.path.normpath
jj = os.path.join

MODEL_ROOT = "/data/sparv/models/stanza"

os.makedirs(jj("tests", "output"), exist_ok=True)

# pylint: disable=redefined-outer-name


def dehyphen(text: str) -> str:
    return text


@fixture(scope="session")
def tagger() -> annotate.StanzaTagger:
    preprocessors: List[Callable[[str], str]] = [dedent, dehyphen, str.strip, pretokenize]
    _tagger: annotate.StanzaTagger = annotate.StanzaTagger(model_root=MODEL_ROOT, preprocessors=preprocessors)
    return _tagger


def test_stanza_annotator_to_document(tagger: annotate.StanzaTagger):
    text: str = "Detta är ett test!"

    tagged_documents: List[stanza.Document] = tagger.tag(text)

    assert len(tagged_documents) == 1
    assert isinstance(tagged_documents[0], stanza.Document) is not None

    assert [w.text for w in tagged_documents[0].iter_words()] == ['Detta', 'är', 'ett', 'test', '!']
    assert [w.lemma for w in tagged_documents[0].iter_words()] == ['detta', 'vara', 'en', 'test', '!']


def test_stanza_annotator_to_csv(tagger: annotate.StanzaTagger):
    text: str = "Hej! Detta är ett test!"

    tagged_documents: List[stanza.Document] = tagger.tag(text)

    assert len(tagged_documents) == 1
    assert isinstance(tagged_documents[0], stanza.Document) is not None

    tagged_csv_str: str = tagger.to_csv(tagged_documents[0])

    assert (
        tagged_csv_str == "text\tlemma\tpos\txpos\n"
        "Hej\thej\tIN\tIN\n"
        "!\t!\tMID\tMID\n"
        "Detta\tdetta\tPN\tPN.NEU.SIN.DEF.SUB+OBJ\n"
        "är\tvara\tVB\tVB.PRS.AKT\n"
        "ett\ten\tDT\tDT.NEU.SIN.IND\n"
        "test\ttest\tNN\tNN.NEU.SIN.IND.NOM\n"
        "!\t!\tMAD\tMAD"
    )


def test_stanza_write_to_zip():
    speech_items = [
        {
            'speech_id': "1",
            'speaker': str(uuid4()),
            'speech_date': "1958-01-01",  # speech.speech_date or
            'speech_index': 1,
            'annotation': str(uuid4()),
            'text': str(uuid4()),
            'document_name': f"{str(uuid4())}",
            'filename': f"{str(uuid4())}.csv",
            'num_tokens': 5,
            'num_words': 5,
        }
    ]

    output_filename: str = jj("tests", "output", f"{str(uuid4())}.zip")

    try:
        annotate.annotate._store_tagged_protocol(output_filename, speech_items)  # pylint: disable=protected-access)
        assert os.path.isfile(output_filename)
    finally:
        os.unlink(output_filename)


def test_stanza_tag_protocol(tagger: annotate.StanzaTagger):

    # Protocol with multiple speeches
    file_data: untangle.Element = untangle.parse(jj("tests", "test_data", "prot-1958-fake.xml"))
    protocol: Protocol = Protocol(file_data)

    assert len(protocol.speeches) == 2
    assert protocol.speeches[0].utterances_segments == [
        ['Hej! Detta är en mening.'],
        ['Jag heter Ove.', 'Vad heter du?'],
    ]

    result: List[Dict[str, Any]] = annotate.tag_protocol(tagger, protocol)

    assert result is not None
    assert len(result) == 2
    assert result[0]['speaker'] == "A"
    assert result[1]['speaker'] == "B"
    assert result[1]['speech_index'] == 2
    assert result[1]['num_tokens'] == 8


def test_stanza_tag_protocol_with_no_speeches(tagger: annotate.StanzaTagger):
    file_data: untangle.Element = untangle.parse(jj("tests", "test_data", "prot-199192--82.xml"))
    protocol: Protocol = Protocol(file_data)
    result = annotate.tag_protocol(tagger, protocol)
    assert result is not None


def test_stanza_annotate_protocol_file_to_zip(tagger: annotate.StanzaTagger):
    input_filename: str = jj("tests", "test_data", "prot-1958-fake.xml")
    output_filename: str = jj("tests", "output", "prot-1958-fake.zip")
    annotate.tag_protocol_xml(input_filename, output_filename, tagger)
    assert os.path.isfile(output_filename)
