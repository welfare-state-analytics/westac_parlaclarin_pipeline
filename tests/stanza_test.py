import os

from workflow.annotate import StanzaAnnotator, annotate_protocol
from workflow.model.tokenize import tokenize

MODEL_ROOT = '/data/sparv/models/stanza'

os.makedirs('tests/output', exist_ok=True)

def test_stanza_annotator_to_document():
    annotator: StanzaAnnotator = StanzaAnnotator()
    text: str = ' '.join(tokenize("Detta är ett test!"))
    result = annotator.to_document(text)

    assert result is not None

    assert [w.text for w in result.iter_words()] == ['Detta', 'är', 'ett', 'test', '!']
    assert [w.lemma for w in result.iter_words()] == ['detta', 'vara', 'en', 'test', '!']


def test_stanza_annotator_to_csv():
    annotator: StanzaAnnotator = StanzaAnnotator()
    text: str = ' '.join(tokenize("Hej! Detta är ett test!"))
    result = annotator.to_csv(text)

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

def test_stanza_annotate_protocol():
    input_filename = 'tests/test_data/prot-1958-fake.xml'
    output_filename = 'tests/output/prot-1958-fake.zip'
    annotator: StanzaAnnotator = StanzaAnnotator()
    annotate_protocol(input_filename, output_filename, annotator)
    assert os.path.isfile(output_filename)


    # data = untangle.parse("tests/test_data/prot-1958-fake.xml")
    # protocol = model.Protocol(data)