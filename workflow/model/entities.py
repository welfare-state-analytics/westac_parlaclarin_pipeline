import re
import textwrap
from typing import List

import untangle
from loguru import logger

from .utility import flatten, hasattr_path, path_add_suffix


class Speech:
    """Wraps ParlaClarin XML utterance tags within a single protocol."""

    def __init__(self, utterances: List[untangle.Element], delimiter: str = '\n', dedent: bool = True):
        """[summary]

        Args:
            utterances (List[untangle.Element]): Utterance tags.
            delimiter (str, optional): Delimiter to use when joining paragraphs. Defaults to '\n'.
            dedent (bool, optional): Remove indentation flag. Defaults to True.

        Raises:
            ValueError: If no utterance was supplied.
        """
        if len(utterances or []) == 0:
            raise ValueError("utterance list cannot be empty")

        self._delimiter = delimiter
        self._dedent = dedent

        self._utterances: List[untangle.Element] = utterances

    def __len__(self):
        return len(self._utterances)

    @property
    def speaker(self):
        try:
            if self._utterances[0].get_attribute('who') is None:
                return "Undefined"
            return self._utterances[0].get_attribute('who')
        except (AttributeError, KeyError):
            return 'Undefined'

    @property
    def speech_id(self):
        """Defined as id of first utterance in speech"""
        return self._utterances[0]['xml:id'] or None

    @property
    def segments(self):
        """The flattened sequence of segments"""
        return flatten(self.utterances_segments)

    paragraphs = segments

    @property
    def utterances_segments(self) -> List[List[str]]:
        """Utterance segments"""
        return [
            [textwrap.dedent(s.cdata) if self._dedent else s.cdata for s in u.get_elements('seg')]
            for u in self._utterances
        ]

    @property
    def utterances(self) -> List[str]:
        """List of utterance texts"""
        return [self._delimiter.join(s) for s in self.utterances_segments]

    @property
    def text(self) -> str:
        """The entire speech text"""
        t = self._delimiter.join(self.paragraphs)
        if t is None:
            raise ValueError("Text cannot be None")
        if not re.search('[a-zåäöA-ZÅÄÖ]', t):
            """Empty string if no letter in text"""
            return ""
        return t


class Protocol:
    """Container that wraps the XML representation of a single ParlaClarin document (protocol)"""

    def __init__(self, data: untangle.Element):
        """
        Args:
            data (untangle.Element): XML document
        """
        self.data: untangle.Element = data
        self.speeches: List[Speech] = SpeechFactory.create(data)

    @property
    def date(self) -> str:
        """Date of protocol"""
        try:
            docDate = self.data.teiCorpus.TEI.text.front.div.docDate
            return docDate[0]['when'] if isinstance(docDate, list) else docDate['when']
        except (AttributeError, KeyError):
            return None

    @property
    def name(self) -> str:
        """Protocol name"""
        try:
            return self.data.teiCorpus.TEI.text.front.div.head.cdata
        except (AttributeError, KeyError):
            return None

    @staticmethod
    def from_file(filename: str) -> "Protocol":
        """Load protocol from `filename`."""
        data = untangle.parse(filename)
        protocol: Protocol = Protocol(data)
        return protocol

    def has_speech_text(self):
        """Checks if any speech actually has any uttered words"""
        for speech in self.speeches:
            if speech.text.strip() != "":
                return True
        return False


class SpeechFactory:
    """Builds speech entities from ParlaClarin XML."""

    @staticmethod
    def create(data: untangle.Element) -> List[Speech]:
        """Create speeches from given XML. Return as list."""
        if not hasattr_path(data, 'teiCorpus.TEI.text.body.div.u'):
            return []

        utterances: List[untangle.Element] = data.teiCorpus.TEI.text.body.div.u
        speeches: List[Speech] = []
        current_speech = []
        for u in utterances:

            if u['prev'] == 'cont':
                if len(current_speech) == 0:
                    raise SyntaxError(f"Unexpected: prev=cont {u['xml:id']}")
                current_speech.append(u)
                continue

            if len(current_speech) > 0:
                speeches.append(Speech(current_speech))

            current_speech = [u]

        if len(current_speech) > 0:
            speech = Speech(current_speech)
            if speech.text != "":
                speeches.append(speech)

        return speeches


class ParlaClarinSpeechTexts:
    """Reads speech xml files and returns a stream of (speech-name, text)"""

    def __init__(self, filenames: List[str]):
        self.filenames = filenames
        self.iterator = None

    def __iter__(self):
        self.iterator = self.create_iterator()
        return self

    def __next__(self):
        return next(self.iterator)

    def create_iterator(self):
        for filename in self.filenames:
            protocol: Protocol = Protocol(data=untangle.parse(filename))
            if len(protocol.speeches) == 0:
                logger.warning(f"protocol {filename} has no speeches!")
                continue
            for speech in protocol.speeches:
                yield path_add_suffix(filename, speech.speech_id), speech.text
