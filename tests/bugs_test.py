import os

from workflow.model import entities as model

jj = os.path.join


def test_parse_xml_with_multiple_speaker_in_same_speech_error():

    filename: str = "/data/riksdagen_corpus_data/riksdagen-corpus/corpus/199192/prot-199192--127.xml"

    protocol: model.Protocol = model.Protocol(filename, remove_empty=False)

    assert protocol is not None
