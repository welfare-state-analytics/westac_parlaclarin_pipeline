import os
from os.path import join as jj
from typing import List
from uuid import uuid4

from workflow import annotate
from workflow.annotate.interface import ITagger, TaggedDocument
from workflow.model import Speech, Utterance


def test_store_tagged_speeches():
    speeches = [
        Speech(
            document_name='prot-1958-fake',
            speech_id='c01',
            speaker='A',
            speech_date='1958',
            speech_index=1,
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
            num_tokens=0,
            num_words=0,
            delimiter='\n',
        )
    ]

    output_filename: str = jj("tests", "output", f"{str(uuid4())}.zip")

    annotate.store_tagged_speeches(
        output_filename, speeches, checksum="sha-1 checksum"
    )  # pylint: disable=protected-access

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
