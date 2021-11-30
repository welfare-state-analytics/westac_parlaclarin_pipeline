import os

from pyriksprot import interface, parlaclarin

jj = os.path.join


def test_parse_xml_with_multiple_speaker_in_same_speech_error():

    filename: str = "/data/riksdagen_corpus_data/riksdagen-corpus/corpus/199192/prot-199192--127.xml"

    protocol: interface.Protocol = parlaclarin.parse.ProtocolMapper.to_protocol(filename, segment_skip_size=0)

    assert protocol is not None
