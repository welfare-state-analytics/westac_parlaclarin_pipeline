import os
import re
import textwrap
from io import StringIO
from typing import Any, Dict, List, Union

import untangle
from loguru import logger

from .utility import flatten, hasattr_path, path_add_suffix, strip_extensions


class Speech:
    """Wraps ParlaClarin XML utterance tags within a single protocol."""

    def __init__(self, utterances: List[untangle.Element], delimiter: str = '\n', dedent: bool = True):
        """[summary]

        Args:
            utterances (List[untangle.Element]): Utterance tags.
            delimiter (str, optional): Delimiter to use when joining paragraphs. Defaults to '\n'.
            dedent (bool, optional): Remove indentation flag. Defaults to True.

        Raises:
            ParlaClarinError: If no utterance was supplied or logical error.
        """
        if len(utterances or []) == 0:
            raise ParlaClarinError("utterance list cannot be empty")

        self._delimiter = delimiter
        self._dedent = dedent

        self._utterances: List[untangle.Element] = utterances

    def add(self, u: untangle.Element) -> "Speech":

        if not all(u['who'] == s['who'] for s in self._utterances):
            raise ParlaClarinError("Multiple speaker in same speech")

        if u['prev'] != self._utterances[0]['xml:id']:
            raise ParlaClarinError("Prev. reference error")

        self._utterances.append(u)
        return self

    def has_utterance(self, u_id: str) -> bool:
        return any(u_id == u.get_attribute('xml:id') for u in self._utterances)

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

    def __init__(self, data: Union[str, untangle.Element], remove_empty=True):
        """
        Args:
            data (untangle.Element): XML document
        """
        self.data: untangle.Element = None
        if isinstance(data, untangle.Element):
            self.data = data
        elif isinstance(data, str):
            if os.path.isfile(data):
                self.data = untangle.parse(data)
            else:
                self.data = untangle.parse(StringIO(data))
        else:
            raise ValueError("invalid data for untangle")

        self.speeches: List[Speech] = SpeechFactory.create(self.data, remove_empty=remove_empty)

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

    def has_speech_text(self) -> bool:
        """Checks if any speech actually has any uttered words"""
        for speech in self.speeches:
            if speech.text.strip() != "":
                return True
        return False

    def to_dict(self, skip_size: int = 5) -> List[Dict[str, Any]]:
        """Extracts text and metadata of non-empty speeches. Returns list."""
        speech_items: List[dict] = []
        speech_index = 1

        for speech in self.speeches:

            text: str = speech.text.strip()

            if not text or len(text) <= (skip_size or 0):
                continue

            speech_items.append(
                dict(
                    speech_id=speech.speech_id,
                    speaker=speech.speaker or "Unknown",
                    speech_date=self.date,  # speech.speech_date or
                    speech_index=speech_index,
                    document_name=f"{strip_extensions(self.name)}@{speech_index}",
                    text=text,
                )
            )
            speech_index += 1

        return speech_items


class ParlaClarinError(ValueError):
    ...


def equal_ids(id1: str, id2: str) -> bool:

    if id1 is not None and id1 is not None:
        return id1.split("-")[1] == id2.split("-")[1]

    return id1 == id2

class SpeechFactory:
    """Construct speech entities from a single ParlaClarin XML. Return list of speeches"""

    @staticmethod
    def create(data: untangle.Element, remove_empty: bool = False) -> List[Speech]:

        if not hasattr_path(data, 'teiCorpus.TEI.text.front.div.head.cdata'):
            logger.warning("teiCorpus.TEI.text.front.div.head.cdata: not found")
            return []

        document_name: str = data.teiCorpus.TEI.text.front.div.head.cdata

        """Create speeches from given XML. Return as list."""
        if not hasattr_path(data, 'teiCorpus.TEI.text.body.div.u'):
            logger.warning(f"{document_name}: no utterance in document")
            return []

        utterances: List[untangle.Element] = data.teiCorpus.TEI.text.body.div.u

        speeches: List[Speech] = []
        speech: Speech = None

        next_id: str = None

        for _, u in enumerate(utterances or []):

            u_id: str = u.get_attribute('xml:id')
            prev_id: str = u.get_attribute('prev')

            if next_id is not None:
                if next_id != u_id:
                    logger.error(f"{document_name}.u[{u_id}]: current u.id differs from previous u.next_id '{next_id}'")

            next_id: str = u.get_attribute('next')

            if prev_id is not None:

                if speech is None:
                    logger.error(f"{document_name}.u[{u_id}]: ignoring prev='{prev_id}' (no previous utterance)")
                    prev_id = None

                if not speech.has_utterance(prev_id):
                    logger.error(f"{document_name}.u[{u_id}]: ignoring prev='{prev_id}' (not found in current speech)")
                    prev_id = None

            if prev_id is None:
                speech = Speech(utterances=[u])
                speeches.append(speech)
            else:
                speeches[-1].add(u)

        if remove_empty:
            speeches = [s for s in speeches if s.text != ""]

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
