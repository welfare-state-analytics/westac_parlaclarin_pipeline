import os
import pickle
from collections import defaultdict
from glob import glob
from typing import Callable, Iterable, List, Union

from tqdm.auto import tqdm

from .entities import ParlaClarinSpeechTexts
from .tokenize import tokenize as default_tokenize
from .utility import logger


class WordFrequencyCounter:
    def __init__(self, tokenize: Callable[[str], List[str]] = None, do_lower_case=True):
        self.tokenize = tokenize or default_tokenize
        self.frequencies = defaultdict(int)
        self.do_lower_case = do_lower_case

    def swallow(self, value: Union[str, Iterable[str], ParlaClarinSpeechTexts]) -> "WordFrequencyCounter":
        texts = (
            (value,)
            if isinstance(value, str)
            else (t for _, t in value)
            if isinstance(value, ParlaClarinSpeechTexts)
            else value
        )
        for text in tqdm(texts):
            if self.do_lower_case:
                text = text.lower()
            for word in self.tokenize(text):
                self.frequencies[word] += 1
        return self

    def store(self, filename: str, cut_off: int = None) -> None:
        if cut_off:
            frequencies = {w: c for w, c in self.frequencies if c > cut_off}
        else:
            frequencies = self.frequencies
        with open(filename, 'wb') as fp:
            pickle.dump(frequencies, fp, pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def load(filename: str) -> defaultdict(int):
        with open(filename, 'rb') as fp:
            return pickle.load(fp)


def compute_word_frequencies(source: Union[str, List[str]], filename: str) -> WordFrequencyCounter:
    try:
        if isinstance(source, ParlaClarinSpeechTexts):
            texts = source
        else:
            if isinstance(source, str):
                if os.path.isfile(source):
                    filenames = [source]
                elif os.path.isdir(source):
                    filenames = glob(os.path.join(source, "*.xml"))
                else:
                    filenames = glob(source)
            elif isinstance(source, list):
                filenames = source
            else:
                raise ValueError(f"unknown source of type {type(source)}")

            texts = ParlaClarinSpeechTexts(filenames)

        counter = WordFrequencyCounter()

        counter.swallow(texts)

        if filename is not None:
            counter.store(filename)

        return counter

    except Exception as ex:
        logger.exception(ex)
        raise
