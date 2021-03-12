import os
import sys
from unittest.mock import Mock, patch

# print(__name__)
# print("CWD: " + os.getcwd())
# print("SYS.PATH: " +':'.join(sys.path))
# print("PYTHONPATH: " + (os.environ.get("PYTHONPATH") or "None"))
# print("APA: " + (os.environ.get("APA") or "None"))
# print("MUPP: " + (os.environ.get("MUPP") or "None"))

try:
    from .. import workflow
    print('Relative import succeeded')
except workflow:
    print('Relative import failed')

try:
    import workflow
    print('Absolute import succeeded')
except ModuleNotFoundError:
    print('Absolute import failed')

import pytest
from workflow.model.dehyphen import FlairDehyphenService
from workflow.model.dehyphen.swe_dehyphen import (
    ParagraphMergeStrategy,
    SwedishDehyphenatorService,
    find_dashed_words,
    get_config_filename,
    merge_paragraphs,
)
from workflow.model.utility import store_dict

#c sys.path.append((lambda d: os.path.join(os.getcwd().split(d)[0], d))("westac_parlaclarin_pipeline"))


TEST_CONFIG = {
    "folders": {
        "work_data_folder": "tests/output",
    },
    "word_frequency": {"filename": 'parla_word_frequencies.pkl'},
    "dehyphen": {
        "whitelist_filename": 'dehyphen_whitelist.txt.gz',
        "unresolved_filename": 'dehyphen_unresolved.txt.gz',
        "whitelist_log_filename": 'dehyphen_whitelist_log.pkl',
    },
}


def test_get_config_filename():
    result = get_config_filename(TEST_CONFIG, "word_frequency.filename")
    assert result == "tests/output/parla_word_frequencies.pkl"

def test_merge_paragraphs():

    text = "Detta är en \n\nmening"
    result = merge_paragraphs(text, ParagraphMergeStrategy.DoNotMerge)
    assert result == text

@pytest.mark.slow
def test_dehyphen_service():

    service = FlairDehyphenService(lang="sv")

    expected_text = "Detta är en\nenkel text.\n\nDen har tre paragrafer.\n\nDetta är den tredje paragrafen."
    dehyphened_text = service.dehyphen_text(expected_text, merge_paragraphs=False)
    assert dehyphened_text == expected_text

    text = "Detta är en\nenkel text.\n\nDen har tre paragrafer.\n   \t\n\n   \nDetta är den tredje paragrafen."
    dehyphened_text = service.dehyphen_text(text, merge_paragraphs=False)
    assert dehyphened_text == expected_text


def test_create_dehyphenator_service_fails_if_no_word_frequency_file():

    word_frequencies_filename = os.path.join(
        TEST_CONFIG['folders']['work_data_folder'], TEST_CONFIG['word_frequency']['filename']
    )

    if os.path.isfile(word_frequencies_filename):
        os.remove(word_frequencies_filename)

    with pytest.raises(FileNotFoundError):
        with patch('workflow.model.dehyphen.swe_dehyphen.SwedishDehyphenator', return_value=Mock()) as _:
            _ = SwedishDehyphenatorService(config=TEST_CONFIG)


def test_create_dehyphenator_service_succeeds_when_frequency_file_exists():

    word_frequencies_filename = os.path.join(
        TEST_CONFIG['folders']['work_data_folder'], TEST_CONFIG['word_frequency']['filename']
    )

    store_dict({}, word_frequencies_filename)

    with patch('workflow.model.dehyphen.swe_dehyphen.SwedishDehyphenator', return_value=Mock()) as mock_dehyphenator:
        _ = SwedishDehyphenatorService(config=TEST_CONFIG)
        mock_dehyphenator.assert_called_once()

    if os.path.isfile(word_frequencies_filename):
        os.remove(word_frequencies_filename)


def test_dehyphenator_service_flush_creates_expected_files():

    word_frequencies_filename = os.path.join(
        TEST_CONFIG['folders']['work_data_folder'], TEST_CONFIG['word_frequency']['filename']
    )

    if os.path.isfile(word_frequencies_filename):
        os.remove(word_frequencies_filename)

    store_dict({}, word_frequencies_filename)

    service = SwedishDehyphenatorService(config=TEST_CONFIG)
    service.flush()

    assert os.path.isfile(service.whitelist_filename)
    assert os.path.isfile(service.whitelist_log_filename)
    assert os.path.isfile(service.unresolved_filename)

    os.remove(service.word_frequencies_filename)
    os.remove(service.whitelist_filename)
    os.remove(service.whitelist_log_filename)
    os.remove(service.unresolved_filename)


def test_dehyphenator_service_can_load_flushed_data():

    word_frequencies_filename = os.path.join(
        TEST_CONFIG['folders']['work_data_folder'], TEST_CONFIG['word_frequency']['filename']
    )

    if os.path.isfile(word_frequencies_filename):
        os.remove(word_frequencies_filename)

    store_dict({}, word_frequencies_filename)

    service = SwedishDehyphenatorService(config=TEST_CONFIG)

    service.dehyphenator.unresolved = {"a", "b", "c"}
    service.dehyphenator.whitelist = {"e", "f", "g"}
    service.dehyphenator.whitelist_log = {"e": 0, "f": 1, "g": 1}

    service.flush()

    assert os.path.isfile(service.whitelist_filename)
    assert os.path.isfile(service.whitelist_log_filename)
    assert os.path.isfile(service.unresolved_filename)

    service2 = SwedishDehyphenatorService(config=TEST_CONFIG)

    assert service2.dehyphenator.whitelist == service.dehyphenator.whitelist
    assert service2.dehyphenator.unresolved == service.dehyphenator.unresolved
    assert service2.dehyphenator.whitelist_log == service.dehyphenator.whitelist_log

    os.remove(service.word_frequencies_filename)
    os.remove(service.whitelist_filename)
    os.remove(service.whitelist_log_filename)
    os.remove(service.unresolved_filename)


def test_find_dashed_words():
    text = "Detta mening har inget binde- streck. Eva-Marie är ett namn. IKEA-möbler. 10-tal. "
    tokens = find_dashed_words(text)
    assert tokens is not None


def test_dehyphenator_service_dehypen():

    dehyphenator = SwedishDehyphenatorService(
        config=TEST_CONFIG,
        word_frequencies=dict(),
        whitelist=set(),
        unresolved=set(),
        whitelist_log=dict(),
    ).dehyphenator
    text = "Detta mening har inget bindestreck."
    result = dehyphenator.dehyphen_text(text)
    assert result == text
    assert len(dehyphenator.whitelist) == 0
    assert len(dehyphenator.unresolved) == 0

    text = "Detta mening har inget binde-streck."
    result = dehyphenator.dehyphen_text(text)
    assert result == text
    assert len(dehyphenator.whitelist) == 0
    assert len(dehyphenator.unresolved) == 0

    text = "Detta mening har ett binde-\nstreck. Eva-Marie är ett namn. IKEA-\nmöbler. 10-\n\ntal. "
    dehyphenator.word_frequencies = {'bindestreck': 1}
    result = dehyphenator.dehyphen_text(text)
    assert result == "Detta mening har ett bindestreck. Eva-Marie är ett namn. IKEA-möbler. 10-tal."
    assert dehyphenator.whitelist == {'bindestreck', 'ikea-möbler', '10-tal'}
    assert len(dehyphenator.unresolved) == 0
