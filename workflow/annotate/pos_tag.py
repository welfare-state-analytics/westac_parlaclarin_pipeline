
import os
import pathlib
import zipfile
from typing import List

import pandas as pd
from stanza.models.common.doc import Document

from ..model.convert import dedent, dehyphen
from ..model.entities import Protocol
from ..model.utility import strip_extensions
from .stanza_tagger import StanzaTagger


def annotate_speeches(tagger: StanzaTagger, protocol: Protocol) -> List[dict]:

    speech_items = []
    speech_index = 1

    for speech in protocol.speeches:

        text: str = dehyphen(dedent(speech.text)).strip()

        if not text:
            continue

        speech_document: Document = tagger.to_document(text)
        speech_csv = tagger.document_to_csv(speech_document)
        document_name = f"{strip_extensions(protocol.name)}@{speech_index}"
        speech_items.append(
            {
                'speech_id': speech.speech_id,
                'speaker': speech.speaker or "Unknown",
                'speech_date': protocol.date,  # speech.speech_date or
                'speech_index': speech_index,
                'annotation': speech_csv,
                'document_name': f"{1}",
                'filename': f"{document_name}.csv",
                'num_tokens': speech_document.num_tokens,
                'num_words': speech_document.num_words,
            }
        )
        speech_index += 1

    return speech_items


def write_to_zip(output_filename: str, speech_items: dict) -> None:

    with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as fp:

        for item in speech_items:
            fp.writestr(item['filename'], item['annotation'])
            del item['annotation']

        document_index_csv: str = pd.DataFrame(speech_items).to_csv(sep='\t', header=True)
        fp.writestr(
            'document_index.csv',
            document_index_csv,
        )


def annotate_protocol(
    input_filename: str = None,
    output_filename: str = None,
    tagger: StanzaTagger = None,
) -> None:

    os.makedirs(os.path.dirname(output_filename), exist_ok=True)

    pathlib.Path(output_filename).unlink(missing_ok=True)

    protocol: Protocol = Protocol.from_file(input_filename)

    if not protocol.has_speech_text():
        pathlib.Path(output_filename).touch(exist_ok=True)
        return

    speech_items = annotate_speeches(tagger, protocol)

    write_to_zip(output_filename, speech_items)
