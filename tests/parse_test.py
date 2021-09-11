import os
from typing import List

import pytest
from workflow.model import model, parse

jj = os.path.join


def test_to_protocol_in_depth_validation_of_correct_parlaclarin_xml():

    protocol: model.Protocol = parse.ProtocolMapper.to_protocol(jj("tests", "test_data", "fake", "prot-1958-fake.xml"))

    assert protocol is not None
    assert len(protocol.utterances) == 4
    assert len(protocol) == 3

    assert protocol.name == 'prot-1958-fake'
    assert protocol.date == '1958'
    assert protocol.has_text(), 'has text'
    assert protocol.checksum(), 'checksum'

    speeches: List[model.Speech] = protocol.to_speeches()
    for i, speech in enumerate(speeches):
        assert speech.speech_date == protocol.date
        assert speech.document_name == protocol.name
        assert speech.speech_name.startswith(protocol.name)
        assert speech.delimiter == '\n'
        assert speech.speech_index == i + 1
        for utterance in speech.utterances:
            assert utterance.who == speech.speaker

    assert speeches[0].text == 'Hej! Detta är en mening.'
    assert speeches[1].text == 'Jag heter Ove.\nVad heter du?'
    assert speeches[2].text == 'Jag heter Adam.\nOve är dum.'

    assert speeches[0] == model.Speech(
        document_name='prot-1958-fake',
        speech_id='c01',
        speaker='A',
        speech_date='1958',
        speech_index=1,
        utterances=[
            model.Utterance(
                n='c01',
                who='A',
                u_id='i-1',
                prev_id=None,
                next_id='i-2',
                paragraphs=['Hej! Detta är en mening.'],
                delimiter='\n',
            )
        ],
        annotation=None,
        num_tokens=0,
        num_words=0,
        delimiter='\n',
    )

    assert speeches[1] == model.Speech(
        document_name='prot-1958-fake',
        speech_id='c02',
        speaker='A',
        speech_date='1958',
        speech_index=2,
        utterances=[
            model.Utterance(
                n='c02',
                who='A',
                u_id='i-2',
                prev_id='i-1',
                next_id=None,
                paragraphs=['Jag heter Ove.', 'Vad heter du?'],
                delimiter='\n',
            )
        ],
        annotation=None,
        num_tokens=0,
        num_words=0,
        delimiter='\n',
    )

    assert speeches[2] == model.Speech(
        document_name='prot-1958-fake',
        speech_id='c03',
        speaker='B',
        speech_date='1958',
        speech_index=3,
        utterances=[
            model.Utterance(
                n='c03', who='B', u_id='i-3', prev_id=None, next_id=None, paragraphs=['Jag heter Adam.'], delimiter='\n'
            ),
            model.Utterance(
                n='c03', who='B', u_id='i-4', prev_id=None, next_id=None, paragraphs=['Ove är dum.'], delimiter='\n'
            ),
        ],
        annotation=None,
        num_tokens=0,
        num_words=0,
        delimiter='\n',
    )


@pytest.mark.parametrize(
    'filename',
    [
        ("prot-197879--14.xml"),
        ("prot-199596--35.xml"),
    ],
)
def test_parse_xml_with_no_utterances(filename):

    protocol = parse.ProtocolMapper.to_protocol(jj("tests", "test_data", "source", filename), skip_size=0)

    assert len(protocol.utterances) == 0, "speech empty"
    assert not protocol.has_text()
