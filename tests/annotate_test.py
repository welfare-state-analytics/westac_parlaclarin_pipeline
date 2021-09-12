import os
from os.path import join as jj
from typing import List
from unittest.mock import Mock
from uuid import uuid4

import pytest
from workflow import annotate
from workflow.annotate.annotate import tag_protocol_xml
from workflow.annotate.interface import ITagger, TaggedDocument
from workflow.model import Protocol, Utterance


@pytest.mark.parametrize('storage_format', ['json', 'csv'])
def test_store_protocols(storage_format: str):
    protocol: Protocol = Protocol(
        name='prot-1958-fake',
        date='1958',
        utterances=[
            Utterance(
                u_id='i-1',
                n='c01',
                who='A',
                prev_id=None,
                next_id='i-2',
                paragraphs=['Hej! Detta är en mening.'],
                annotation="token\tpos\tlemma\nA\ta\tNN",
                delimiter='\n',
            )
        ],
    )

    output_filename: str = jj("tests", "output", f"{str(uuid4())}.zip")

    annotate.store_protocol(
        output_filename,
        protocol=protocol,
        storage_format=storage_format,
        checksum='apa',
    )

    assert os.path.isfile(output_filename)

    metadata: dict = annotate.load_metadata(output_filename)

    assert metadata is not None

    loaded_protocol: Protocol = annotate.load_protocol(output_filename)

    assert protocol.name == loaded_protocol.name
    assert protocol.date == loaded_protocol.date
    assert [u.__dict__ for u in protocol.utterances] == [u.__dict__ for u in loaded_protocol.utterances]

    # os.unlink(output_filename)


def test_tag_protocol_xml():
    def tag(text: str, preprocess: bool):  # pylint: disable=unused-argument
        return [
            dict(
                token=['Ove', 'är', 'dum', '.'],
                lemma=['ove', 'vara', 'dum', '.'],
                pos=['PM', 'VB', 'ADJ', 'MAD'],
                xpos=['PM', 'VB', 'ADJ', 'MAD'],
                num_tokens=3,
                num_words=3,
            )
        ]

    tagger: ITagger = Mock(spec=ITagger, tag=tag, to_csv=ITagger.to_csv, preprocess=lambda x: x)

    input_filename: str = jj("tests", "test_data", "fake", "prot-1958-fake.xml")
    output_filename: str = jj("tests", "output", f"{str(uuid4())}.zip")

    tag_protocol_xml(input_filename=input_filename, output_filename=output_filename, tagger=tagger)

    assert os.path.isfile(output_filename)

    os.unlink(output_filename)


def test_to_csv():

    tagged_documents: List[TaggedDocument] = [
        {
            'lemma': ['hej', '!', 'detta', 'vara', 'en', 'test', '!'],
            'num_tokens': 7,
            'num_words': 7,
            'pos': ['IN', 'MID', 'PN', 'VB', 'DT', 'NN', 'MAD'],
            'token': ['Hej', '!', 'Detta', 'är', 'ett', 'test', '!'],
            'xpos': [
                'IN',
                'MID',
                'PN.NEU.SIN.DEF.SUB+OBJ',
                'VB.PRS.AKT',
                'DT.NEU.SIN.IND',
                'NN.NEU.SIN.IND.NOM',
                'MAD',
            ],
        }
    ]

    tagged_csv_str: str = ITagger.to_csv(tagged_documents[0])

    assert (
        tagged_csv_str == "token\tlemma\tpos\txpos\n"
        "Hej\thej\tIN\tIN\n"
        "!\t!\tMID\tMID\n"
        "Detta\tdetta\tPN\tPN.NEU.SIN.DEF.SUB+OBJ\n"
        "är\tvara\tVB\tVB.PRS.AKT\n"
        "ett\ten\tDT\tDT.NEU.SIN.IND\n"
        "test\ttest\tNN\tNN.NEU.SIN.IND.NOM\n"
        "!\t!\tMAD\tMAD"
    )
