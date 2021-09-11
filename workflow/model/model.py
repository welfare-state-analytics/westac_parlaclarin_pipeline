import abc
import contextlib
import hashlib
import re
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Callable, List, Literal, Mapping, Optional, Union

from loguru import logger

from .utility.utils import deprecated, flatten, strip_extensions


class ParlaClarinError(ValueError):
    ...


@dataclass
class Utterance:
    """A processed speech entity"""

    n: str = ""
    who: str = None
    u_id: str = None
    prev_id: int = None
    next_id: str = None
    paragraphs: List[str] = field(default_factory=list)
    delimiter: str = field(default='\n')

    @property
    def text(self) -> str:
        return self.delimiter.join(p for p in self.paragraphs if p != '').strip()


@dataclass
class Speech:
    """A processed speech entity"""

    document_name: str
    speech_id: str
    speaker: str
    speech_date: str
    speech_index: int

    utterances: List[Utterance] = field(default_factory=list)

    annotation: str = None
    num_tokens: int = 0
    num_words: int = 0

    delimiter: str = field(default='\n')

    # self.dedent: bool = True

    def __post_init__(self):

        if len(self.utterances or []) == 0:
            raise ParlaClarinError("utterance list cannot be empty")

        if any(self.speaker != u.who for u in self.utterances):
            raise ParlaClarinError("multiple speakes in same speech not allowed")

    # @property
    # def speech_id(self) -> Optional[str]:
    #     """Defined as id of first utterance in speech"""
    #     if len(self.utterances) == 0:
    #         return None
    #     return self.utterances[0].n
    # n = speech_id

    @property
    def filename(self):
        return f"{self.speech_name}.csv"

    @property
    def speech_name(self):
        return f"{strip_extensions(self.document_name)}@{self.speech_index}"

    @property
    def text(self):
        """The entire speech text"""
        t: str = self.delimiter.join(t for t in (u.text for u in self.utterances) if t != '')
        if not re.search('[a-zåäöA-ZÅÄÖ]', t):
            """Empty string if no letter in text"""
            return ""
        return t.strip()

    def __len__(self):
        return len(self.utterances)

    def __contains__(self, item: Union[str, Utterance]) -> bool:
        if isinstance(item, Utterance):
            item = item.u_id
        return any(u.u_id == item for u in self.utterances)

    @property
    def paragraphs(self) -> Optional[str]:
        """The flattened sequence of segments"""
        return flatten(u.paragraphs for u in self.utterances)


#     @property
#     def paragraph_texts(self) -> List[List[str]]:
#         """Utterance segments"""
#         return [u.paragraphs for u in self.utterances]

#     @property
#     def utterance_texts(self) -> List[str]:
#         """List of utterance texts"""
#         return [self.delimiter.join(s) for s in self.paragraph_texts]


@dataclass
class Protocol:

    date: str
    name: str

    utterances: List[Utterance]  # = field(default_factory=list)

    def has_text(self) -> bool:
        """Checks if any utterance actually has any uttered words"""
        return any(utterance.text != "" for utterance in self.utterances)

    def preprocess(self, preprocess: Callable[[str], str] = None) -> "Protocol":
        """Extracts text and metadata of non-empty speeches. Returns list of dicts."""

        if preprocess is None:
            return self

        for utterance in self.utterances:
            utterance.paragraphs = [preprocess(p.strip()) for p in utterance.paragraphs]

        return self

    def checksum(self) -> Optional[str]:
        with contextlib.suppress(Exception):
            return hashlib.sha1(''.join(u.text for u in self.utterances).encode('utf-8')).hexdigest()
        return None

    @property
    def text(self) -> str:
        return '\n'.join(u.text for u in self.utterances).strip()

    def __len__(self):
        return len(self.utterances)

    def to_speeches(self, merge_strategy: Literal['n', 'who', 'chain'] = 'n', skip_size: int = 1) -> List[Speech]:

        speeches: List[Speech] = SpeechMergerFactory.get(merge_strategy).speeches(self, skip_size=skip_size)
        return speeches


class IMergeSpeechStrategy(abc.ABC):
    def to_speech(self, protocol: Protocol, utterances: List[Utterance], speech_index: int) -> Speech:
        """Create a new speech entity."""
        return Speech(
            document_name=protocol.name,
            speech_id=utterances[0].u_id,  # FIXME
            speaker=utterances[0].who,
            speech_date=protocol.date,
            speech_index=speech_index,
            utterances=utterances,
        )

    def speeches(self, protocol: Protocol, skip_size: int = 1) -> List[Speech]:

        speeches: List[Speech] = self.merge(protocol=protocol)

        if skip_size > 0:
            speeches = [s for s in speeches if len(s.text or "") >= skip_size]

        return speeches

    @abc.abstractmethod
    def merge(self, protocol: Protocol) -> List[Speech]:
        return []


class MergeSpeechById(IMergeSpeechStrategy):
    def merge(self, protocol: Protocol) -> List[Speech]:
        """Create a speech per unique u:n value. Return list of Speech."""
        data = defaultdict(list)
        for u in protocol.utterances:
            data[u.n].append(u)
        return [self.to_speech(protocol, utterances=data[n], speech_index=i + 1) for i, n in enumerate(data)]


class MergeSpeechByWho(IMergeSpeechStrategy):
    def merge(self, protocol: Protocol) -> List[Speech]:
        """Create a speech per unique speaker. Return list of Speech."""
        data = defaultdict(list)
        for u in protocol.utterances:
            data[u.who].append(u)
        return [self.to_speech(protocol, utterances=data[who], speech_index=i + 1) for i, who in enumerate(data)]


class MergeSpeechByChain(IMergeSpeechStrategy):
    @deprecated
    def merge(self, protocol: Protocol) -> List[Speech]:
        """Create speeches based on prev/next chain. Return list."""
        speeches: List[Speech] = []
        speech: Speech = None

        next_id: str = None

        for _, u in enumerate(protocol.utterances or []):

            prev_id: str = u.prev_id

            if next_id is not None:
                if next_id != u.u_id:
                    logger.error(
                        f"{protocol.name}.u[{u.u_id}]: current u.id differs from previous u.next_id '{next_id}'"
                    )

            next_id: str = u.next_id

            if prev_id is not None:

                if speech is None:
                    logger.error(f"{protocol.name}.u[{u.u_id}]: ignoring prev='{prev_id}' (no previous utterance)")
                    prev_id = None

                else:
                    if not speech.has_utterance(prev_id):
                        logger.error(
                            f"{protocol.name}.u[{u.u_id}]: ignoring prev='{prev_id}' (not found in current speech)"
                        )
                        prev_id = None

            if prev_id is None:
                speech = self.to_speech(protocol, utterances=[u], speech_index=len(speeches) + 1)
                speeches.append(speech)
            else:
                speeches[-1].add(u)

        return speeches


class SpeechMergerFactory:
    class UndefinedMergeSpeech(IMergeSpeechStrategy):
        def merge(self, protocol: Protocol) -> List[Speech]:
            return []

    strategies: Mapping[Literal['n', 'who', 'chain'], "IMergeSpeechStrategy"] = {
        'n': MergeSpeechById(),
        'who': MergeSpeechByWho(),
        'chain': MergeSpeechByChain(),
    }

    undefined = UndefinedMergeSpeech()

    @staticmethod
    def get(strategy: str) -> IMergeSpeechStrategy:
        return SpeechMergerFactory.strategies.get(strategy, SpeechMergerFactory.undefined)
