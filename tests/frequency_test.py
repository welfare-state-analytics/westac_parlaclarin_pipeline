import os

import pytest
from workflow.model import WordFrequencyCounter
from workflow.model.compute import compute_word_frequencies
from workflow.model.entities import ParlaClarinSpeechTexts
from workflow.model.utility.utils import temporary_file

jj = os.path.join


def test_parla_clarin_swallow():
    filenames = [jj("tests", "test_data", "prot-199293--72.xml")]
    texts = ParlaClarinSpeechTexts(filenames)
    i = 0
    for text in texts:
        assert len(text) > 0
        i += 1
    assert i > 0


@pytest.mark.parametrize('text', ["a a b c c d e f a e", ["a a b c c", "d e f a e"]])
def test_word_frequency_counter(text):

    counter: WordFrequencyCounter = WordFrequencyCounter()

    counter.swallow(text)

    assert counter.frequencies.get('a', None) == 3
    assert counter.frequencies.get('b', None) == 1
    assert counter.frequencies.get('c', None) == 2
    assert counter.frequencies.get('d', None) == 1
    assert counter.frequencies.get('e', None) == 2
    assert counter.frequencies.get('f', None) == 1


def test_word_frequency_counter_swallow_parla_clarin_files():
    filenames = [jj("tests", "test_data", "prot-199293--72.xml")]
    texts = ParlaClarinSpeechTexts(filenames)
    counter: WordFrequencyCounter = WordFrequencyCounter()

    counter.swallow(texts)

    assert len(counter.frequencies) > 0


def test_persist_word_frequencies():

    filenames = [jj("tests", "test_data", "prot-199293--72.xml")]
    texts = ParlaClarinSpeechTexts(filenames)
    counter: WordFrequencyCounter = WordFrequencyCounter()

    counter.swallow(texts)

    store_name = jj("tests", "output", "test_persist_word_frequencies.pkl")
    counter.store(store_name)

    assert os.path.isfile(store_name)

    wf = WordFrequencyCounter.load(store_name)
    assert counter.frequencies == wf

    # os.unlink(store_name)


def test_compute_word_frequencies():

    with temporary_file(filename=jj("tests", "output", "test_compute_word_frequencies.pkl")) as store_name:
        filenames = [jj("tests", "test_data", "prot-199293--72.xml")]
        compute_word_frequencies(source=filenames, filename=store_name)
        assert os.path.isfile(store_name)
