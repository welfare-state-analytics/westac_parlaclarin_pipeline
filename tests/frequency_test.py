import os
from typing import List

import pytest
from workflow.model import TermFrequencyCounter, parse
from workflow.model.term_frequency import compute_term_frequencies
from workflow.model.utility.utils import temporary_file

jj = os.path.join

TEST_PARLACLARIN_XML_FILES = [
    ("prot-1933--fk--5.xml", 1),
    ("prot-1955--ak--22.xml", 79),
    ("prot-197879--14.xml", 0),
    ("prot-199596--35.xml", 0),
]


@pytest.mark.parametrize('filename, expected_count', TEST_PARLACLARIN_XML_FILES)
def test_parla_clarin_iterator(filename: str, expected_count: int):
    texts_iter = parse.ParlaClarinSpeechTexts([jj("./tests/test_data/source", filename)])
    texts = [t for t in texts_iter]
    assert all(len(t) > 0 for t in texts)
    assert expected_count == len(texts)


@pytest.mark.parametrize('text', ["a a b c c d e f a e", ["a a b c c", "d e f a e"]])
def test_word_frequency_counter(text):

    counter: TermFrequencyCounter = TermFrequencyCounter()

    counter.ingest(text)

    assert counter.frequencies.get('a', None) == 3
    assert counter.frequencies.get('b', None) == 1
    assert counter.frequencies.get('c', None) == 2
    assert counter.frequencies.get('d', None) == 1
    assert counter.frequencies.get('e', None) == 2
    assert counter.frequencies.get('f', None) == 1


@pytest.mark.parametrize('filename', [f[0] for f in TEST_PARLACLARIN_XML_FILES])
def test_word_frequency_counter_ingest_parla_clarin_files(filename: str):
    path: str = jj("tests", "test_data", "source", filename)

    texts = parse.ParlaClarinSpeechTexts([path])
    counter: TermFrequencyCounter = TermFrequencyCounter()
    protocol: parse.Protocol = parse.Protocol(path)

    counter.ingest(texts)

    assert protocol.has_speech_text() == (len(counter.frequencies) > 0)


@pytest.mark.parametrize('filename', [f[0] for f in TEST_PARLACLARIN_XML_FILES[:1]])
def test_persist_word_frequencies(filename: List[str]):
    path: str = jj("tests", "test_data", "source", filename)

    texts = parse.ParlaClarinSpeechTexts([path])
    counter: TermFrequencyCounter = TermFrequencyCounter()

    counter.ingest(texts)

    store_name = jj("tests", "output", "test_persist_word_frequencies.pkl")
    counter.store(store_name)

    assert os.path.isfile(store_name)

    wf = TermFrequencyCounter.load(store_name)
    assert counter.frequencies == wf

    # os.unlink(store_name)


@pytest.mark.parametrize(
    'filename,expected_frequencies',
    [
        (
            'prot-1958-fake.xml',
            {
                'hej': 1,
                '!': 1,
                'detta': 1,
                'är': 2,
                'en': 1,
                'mening': 1,
                '.': 4,
                'jag': 2,
                'heter': 3,
                'ove': 2,
                'vad': 1,
                'du': 1,
                '?': 1,
                'adam': 1,
                'dum': 1,
            },
        )
    ],
)
def test_compute_word_frequencies(filename: str, expected_frequencies: dict):

    filenames: List[str] = [jj('./tests/test_data/fake', filename)]
    with temporary_file(filename=jj("tests", "output", "test_compute_word_frequencies.pkl")) as store_name:
        counts: TermFrequencyCounter = compute_term_frequencies(source=filenames, filename=store_name)
        assert os.path.isfile(store_name)

    assert dict(counts.frequencies) == expected_frequencies
