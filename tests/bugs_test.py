import os

from workflow.model import parse

jj = os.path.join


def test_parse_xml_with_multiple_speaker_in_same_speech_error():

    filename: str = "/data/riksdagen_corpus_data/riksdagen-corpus/corpus/199192/prot-199192--127.xml"

    protocol: parse.Protocol = parse.Protocol(filename, remove_empty=False)

    assert protocol is not None
