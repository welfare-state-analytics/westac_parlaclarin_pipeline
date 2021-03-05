from typing import List
from workflow.model.utility import flatten

import untangle


class Speech:
    def __init__(self, utterances: List[untangle.Element], delimiter: str = '\n'):
        self.delimiter = delimiter
        self._speaker = utterances[0]['who'] if len(utterances) > 0 and 'who' in utterances[0] else 'unknown'
        self._utterances: List[untangle.Element] = utterances

    def __len__(self):
        return len(self._utterances)

    @property
    def speaker(self):
        return self._utterances[0]['who'] or "Undefined"

    @property
    def speech_id(self):
        """Defined as id of first utterance in speech"""
        return self._utterances[0]['xml:id'] or None

    @property
    def segments(self):
        """The flattened sequence of segments"""
        return flatten(self.utterances_segments)

    def paragraphs(self) -> List[str]:
        """The flattened sequence of segments"""
        return self.segments

    @property
    def utterances_segments(self) -> List[List[str]]:
        """Utterance segments"""
        return [[s.cdata for s in u.seg] if isinstance(u.seg, list) else [u.seg.cdata] for u in self._utterances]

    @property
    def utterances(self) -> List[str]:
        """List of utterance texts"""
        return [self.delimiter.join(s) for s in self.utterances_segments]

    @property
    def text(self) -> str:
        """The entire speech text"""
        return self.delimiter.join(self.paragraphs)


class Protocol:

    """Container for a single `Riksdagens protokoll`"""

    def __init__(self, data: untangle.Element):
        self._speeches = MergeSpeeches().merge(data.teiCorpus.TEI.text.body.div.u)

    @property
    def speeches(
        self,
    ) -> List[Speech]:
        return self._speeches

    @staticmethod
    def from_file(filename: str) -> "Protocol":
        data = untangle.parse(filename)
        protocol: Protocol = Protocol(data)
        return protocol


class MergeSpeeches:
    def merge(self, utterances: List[untangle.Element]) -> List[Speech]:

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
            speeches.append(Speech(current_speech))

        return speeches
