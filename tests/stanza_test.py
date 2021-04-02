import os
from uuid import uuid4

import untangle
from workflow.annotate import StanzaTagger, annotate_protocol, document_to_csv, tag_speeches, write_to_zip
from workflow.model.convert import dedent, pretokenize
from workflow.model.entities import Protocol

nj = os.path.normpath
jj = os.path.join

MODEL_ROOT = "/data/sparv/models/stanza"

os.makedirs(jj("tests", "output"), exist_ok=True)


def dehyphen(text: str) -> str:
    return text


def test_stanza_annotator_to_document():
    preprocessors = [dedent, dehyphen, str.strip, pretokenize]
    tagger: StanzaTagger = StanzaTagger(model_root=MODEL_ROOT, preprocessors=preprocessors)
    text: str = "Detta är ett test!"
    result = tagger.tag(text)

    assert result is not None

    assert [w.text for w in result.iter_words()] == ['Detta', 'är', 'ett', 'test', '!']
    assert [w.lemma for w in result.iter_words()] == ['detta', 'vara', 'en', 'test', '!']


def test_stanza_annotator_to_csv():
    preprocessors = [dedent, dehyphen, str.strip, pretokenize]
    tagger: StanzaTagger = StanzaTagger(model_root=MODEL_ROOT, preprocessors=preprocessors)
    text: str = "Hej! Detta är ett test!"
    document = tagger.tag(text)
    result = document_to_csv(document)
    assert (
        result == "text\tlemma\tpos\txpos\n"
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
            'document_name': f"{str(uuid4())}",
            'filename': f"{str(uuid4())}.csv",
            'num_tokens': 5,
            'num_words': 5,
        }
    ]

    output_filename = jj("tests", "output", f"{str(uuid4())}.zip")

    write_to_zip(output_filename, speech_items)
    assert os.path.isfile(output_filename)
    os.unlink(output_filename)


def test_stanza_annotate_protocol():

    file_data = untangle.parse(jj("tests", "test_data", "prot-1958-fake.xml"))
    protocol = Protocol(file_data)

    preprocessors = [dedent, dehyphen, str.strip, pretokenize]
    tagger: StanzaTagger = StanzaTagger(model_root=MODEL_ROOT, preprocessors=preprocessors)
    result = tag_speeches(tagger, protocol)
    assert result is not None
    assert len(result) == 2
    assert result[0]['speaker'] == "A"
    assert result[1]['speaker'] == "B"
    assert result[1]['speech_index'] == 2
    assert result[1]['num_tokens'] == 8


def test_stanza_annotate_protocol_file_to_zip():
    input_filename = jj("tests", "test_data", "prot-1958-fake.xml")
    output_filename = jj("tests", "output", "prot-1958-fake.zip")
    preprocessors = [dedent, dehyphen, str.strip, pretokenize]
    tagger: StanzaTagger = StanzaTagger(model_root=MODEL_ROOT, preprocessors=preprocessors)
    annotate_protocol(input_filename, output_filename, tagger)
    assert os.path.isfile(output_filename)
