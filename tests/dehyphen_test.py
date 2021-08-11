import os
import pickle
from unittest.mock import Mock, patch

import pytest
from workflow.config import Config, load_typed_config
from workflow.model.dehyphenation.swe_dehyphen import (
    ParagraphMergeStrategy,
    SwedishDehyphenatorService,
    find_dashed_words,
    merge_paragraphs,
)
from workflow.model.utility.utils import temporary_file

jj = os.path.join
nj = os.path.normpath
# sys.path.append((lambda d: os.path.join(os.getcwd().split(d)[0], d))("westac_parlaclarin_pipeline"))

# pylint: disable=redefined-outer-name

os.makedirs(jj("tests", "output"), exist_ok=True)


def test_word_frequency_file_path():
    _config: Config = load_typed_config("test_config.yml")
    _config.data_folder = jj("tests", "output")
    result = jj(_config.work_folders.data_folder, _config.word_frequency.filename)
    expected_path: str = jj("tests", "output", "riksdagen-corpus-term-frequencies.pkl")
    assert result == expected_path
    assert _config.word_frequency.file_path == expected_path


def test_merge_paragraphs():

    text = "Detta är en \n\nmening"
    result = merge_paragraphs(text, ParagraphMergeStrategy.DoNotMerge)
    assert result == text


# @pytest.mark.slow
# def test_dehyphen_service():

#     service = FlairDehyphenService(lang="sv")

#     expected_text = "Detta är en\nenkel text.\n\nDen har tre paragrafer.\n\nDetta är den tredje paragrafen."
#     dehyphened_text = service.dehyphen_text(expected_text, merge_paragraphs=False)
#     assert dehyphened_text == expected_text

#     text = "Detta är en\nenkel text.\n\nDen har tre paragrafer.\n   \t\n\n   \nDetta är den tredje paragrafen."
#     dehyphened_text = service.dehyphen_text(text, merge_paragraphs=False)
#     assert dehyphened_text == expected_text


def test_create_dehyphenator_service_fails_if_no_word_frequency_file():
    _config: Config = load_typed_config("test_config.yml")
    _config.data_folder = jj("tests", "output")
    if os.path.isfile(_config.word_frequency.file_path):
        os.remove(_config.word_frequency.file_path)

    with pytest.raises(FileNotFoundError):
        with patch('workflow.model.dehyphenation.swe_dehyphen.SwedishDehyphenator', return_value=Mock()) as _:
            _ = SwedishDehyphenatorService(config=_config)


def test_create_dehyphenator_service_succeeds_when_frequency_file_exists():
    _config: Config = load_typed_config("test_config.yml")
    _config.data_folder = jj("tests", "output")
    with temporary_file(filename=_config.word_frequency.file_path, content=pickle.dumps({'a': 1})):
        with patch(
            'workflow.model.dehyphenation.swe_dehyphen.SwedishDehyphenator', return_value=Mock()
        ) as mock_dehyphenator:
            _ = SwedishDehyphenatorService(config=_config)
            mock_dehyphenator.assert_called_once()


def test_dehyphenator_service_flush_creates_expected_files():
    _config: Config = load_typed_config("test_config.yml")
    _config.data_folder = jj("tests", "output")
    with temporary_file(filename=_config.word_frequency.file_path, content=pickle.dumps({'a': 1})):

        service = SwedishDehyphenatorService(config=_config)

        service.flush()

        assert os.path.isfile(service.config.dehyphen.whitelist_path)
        assert os.path.isfile(service.config.dehyphen.unresolved_path)
        assert os.path.isfile(service.config.dehyphen.whitelist_log_path)

        os.remove(service.config.dehyphen.whitelist_path)
        os.remove(service.config.dehyphen.unresolved_path)
        os.remove(service.config.dehyphen.whitelist_log_path)


def test_dehyphenator_service_can_load_flushed_data():

    _config: Config = load_typed_config("test_config.yml")
    _config.data_folder = jj("tests", "output")

    with temporary_file(filename=_config.word_frequency.file_path, content=pickle.dumps({'a': 1})):

        service = SwedishDehyphenatorService(config=_config)

        service.dehyphenator.unresolved = {"a", "b", "c"}
        service.dehyphenator.whitelist = {"e", "f", "g"}
        service.dehyphenator.whitelist_log = {"e": 0, "f": 1, "g": 1}

        service.flush()

        assert os.path.isfile(service.config.dehyphen.whitelist_path)
        assert os.path.isfile(service.config.dehyphen.unresolved_path)
        assert os.path.isfile(service.config.dehyphen.whitelist_log_path)

        service2 = SwedishDehyphenatorService(config=_config)

        assert service2.dehyphenator.whitelist == service.dehyphenator.whitelist
        assert service2.dehyphenator.unresolved == service.dehyphenator.unresolved
        assert service2.dehyphenator.whitelist_log == service.dehyphenator.whitelist_log

        os.remove(service.config.dehyphen.whitelist_path)
        os.remove(service.config.dehyphen.unresolved_path)
        os.remove(service.config.dehyphen.whitelist_log_path)


def test_find_dashed_words():
    text = "Detta mening har inget binde- streck. Eva-Marie är ett namn. IKEA-möbler. 10-tal. "
    tokens = find_dashed_words(text)
    assert tokens is not None


def test_dehyphenator_service_dehyphen():

    _config: Config = load_typed_config("test_config.yml")
    _config.data_folder = jj("tests", "output")

    dehyphenator = SwedishDehyphenatorService(
        config=_config,
        word_frequencies={'a': 1},
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
    dehyphenator.word_frequencies = {'bindestreck': 2, 'binde-streck': 1}
    result = dehyphenator.dehyphen_text(text)
    assert result == "Detta mening har ett bindestreck. Eva-Marie är ett namn. IKEA-möbler. 10-tal."
    assert dehyphenator.whitelist == {'bindestreck', 'ikea-möbler', '10-tal'}
    assert len(dehyphenator.unresolved) == 0


def test_dehyphenator_service_dehyphen_by_frequency():
    _config: Config = load_typed_config("test_config.yml")
    _config.data_folder = jj("tests", "output")

    dehyphenator = SwedishDehyphenatorService(
        config=_config,
        word_frequencies={'a': 1},
        whitelist=set(),
        unresolved=set(),
        whitelist_log=dict(),
    ).dehyphenator

    text = "Detta är ett binde-\nstreck. "
    dehyphenator.word_frequencies = {'bindestreck': 1, 'binde-streck': 2}
    result = dehyphenator.dehyphen_text(text)
    assert result == "Detta är ett binde-streck."
    assert dehyphenator.whitelist == {'binde-streck'}
    assert len(dehyphenator.unresolved) == 0
