import os
from typing import List

import pytest
import untangle
from workflow.model import parse
from workflow.model.model import Protocol, Speech, Utterance

jj = os.path.join


def test_to_speeches_in_depth_validation_of_correct_parlaclarin_xml():

    protocol: Protocol = parse.ProtocolMapper.to_protocol(jj("tests", "test_data", "fake", "prot-1958-fake.xml"))

    assert protocol is not None
    assert len(protocol.utterances) == 4
    assert len(protocol) == 3

    assert protocol.name == 'prot-1958-fake'
    assert protocol.date == '1958'
    assert protocol.has_text(), 'has text'
    assert protocol.checksum(), 'checksum'

    speeches: List[Speech] = protocol.to_speeches()
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

    assert speeches[0] == Speech(
        document_name='prot-1958-fake',
        speech_id='c01',
        speaker='A',
        speech_date='1958',
        speech_index=1,
        utterances=[
            Utterance(
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

    assert speeches[1] == Speech(
        document_name='prot-1958-fake',
        speech_id='c02',
        speaker='A',
        speech_date='1958',
        speech_index=2,
        utterances=[
            Utterance(
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

    assert speeches[2] == Speech(
        document_name='prot-1958-fake',
        speech_id='c03',
        speaker='B',
        speech_date='1958',
        speech_index=3,
        utterances=[
            Utterance(
                n='c03', who='B', u_id='i-3', prev_id=None, next_id=None, paragraphs=['Jag heter Adam.'], delimiter='\n'
            ),
            Utterance(
                n='c03', who='B', u_id='i-4', prev_id=None, next_id=None, paragraphs=['Ove är dum.'], delimiter='\n'
            ),
        ],
        annotation=None,
        num_tokens=0,
        num_words=0,
        delimiter='\n',
    )


@pytest.mark.parametrize(
    'filename, speech_count, non_empty_speech_count, strategy',
    [
        ("prot-1933--fk--5.xml", 1, 1, 'chain'),
        ("prot-1955--ak--22.xml", 82, 79, 'chain'),
        ('prot-199192--127.xml', 206, 206, 'chain'),
        ("prot-1933--fk--5.xml", 1, 1, 'n'),
        ("prot-1955--ak--22.xml", 33, 33, 'n'),
        ('prot-199192--127.xml', 206, 51, 'n'),
        ("prot-1933--fk--5.xml", 1, 1, 'who'),
        ("prot-1955--ak--22.xml", 33, 33, 'who'),
        ('prot-199192--127.xml', 51, 51, 'who'),
    ],
)
def test_protocol_to_speeches_with_different_strategies(filename: str, speech_count: int, non_empty_speech_count: int, strategy: str):

    protocol: Protocol = parse.ProtocolMapper.to_protocol(filename, skip_size=0)

    speeches = protocol.to_speeches(merge_strategy=strategy, skip_size=0)
    assert len(speeches) == speech_count, "speech count"

    protocol: Protocol = parse.ProtocolMapper.to_protocol(filename, skip_size=1)
    speeches = protocol.to_speeches(merge_strategy=strategy, skip_size=1)
    assert len(speeches) == non_empty_speech_count

    assert all(x.text != "" for x in speeches)
    assert os.path.splitext(filename)[0] == protocol.name
    assert protocol.date is not None
    assert protocol.has_text() == any(x.text != "" for x in speeches)

    protocol: Protocol = parse.ProtocolMapper.to_protocol(filename)
    speeches = protocol.to_speeches(merge_strategy=strategy, skip_size=3)
    assert all(len(x.text) > 3 for x in speeches)

    protocol: Protocol = parse.ProtocolMapper.to_protocol(filename)
    speeches = protocol.to_speeches(merge_strategy=strategy, skip_size=100)
    assert all(len(x.text) > 100 for x in speeches)


@pytest.mark.parametrize(
    'filename, expected_speech_count',
    [
        ('prot-199192--21.xml', 0),
    ],
)
def test_to_speeches_with_faulty_attribute(filename, expected_speech_count):

    data = untangle.parse(jj("tests", "test_data", "source", filename))

    protocol = parse.ProtocolMapper.to_protocol(data, skip_size=0)
    speeches = protocol.to_speeches(merge_strategy='n')
    assert len(speeches) != expected_speech_count, "speech length"
