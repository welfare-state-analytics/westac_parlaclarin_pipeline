import os

import pytest
from pyriksprot import interface
from pyriksprot.corpus import parlaclarin

jj = os.path.join


@pytest.mark.skipif(os.environ.get("RIKSPROT_DATA_FOLDER") is None, reason="no data")
def test_parse_xml_with_multiple_speaker_in_same_speech_error():

    # filename: str = jj(
    #     os.environ["RIKSPROT_DATA_FOLDER"], "riksdagen-corpus/corpus/protocols/199192/prot-199192--127.xml"
    # )

    filename: str = jj(
        os.environ["RIKSPROT_DATA_FOLDER"], "riksdagen-corpus/corpus/protocols/1911/prot-1911--ak--48.xml"
    )

    protocol: interface.Protocol = parlaclarin.parse.ProtocolMapper.parse(filename)

    assert protocol is not None
