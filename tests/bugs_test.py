import os

import pytest
from pyriksprot import interface
from pyriksprot.corpus import parlaclarin

jj = os.path.join


@pytest.mark.skipif(os.environ.get("CORPUS_REPOSITORY_FOLDER") is None, reason="no data")
def test_parse_xml_with_multiple_speaker_in_same_speech_error():

    filename: str = jj(os.environ["CORPUS_REPOSITORY_FOLDER"], "corpus/protocols/199192/prot-199192--127.xml")

    protocol: interface.Protocol = parlaclarin.parse.ProtocolMapper.to_protocol(filename, segment_skip_size=0)

    assert protocol is not None
