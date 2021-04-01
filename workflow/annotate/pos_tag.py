import os
import pathlib
import zipfile
from typing import List

import pandas as pd
from stanza.models.common.doc import Document

from ..model.entities import Protocol
from ..model.utility import strip_extensions
from .stanza_tagger import StanzaTagger


def document_to_csv(tagged_document: Document, sep='\t') -> str:
    """Converts a stanza.Document to a TSV string"""
    csv_str = '\n'.join(f"{w.text}{sep}{w.lemma}{sep}{w.upos}{sep}{w.xpos}" for w in tagged_document.iter_words())
    csv_str = f"text{sep}lemma{sep}pos{sep}xpos\n{csv_str}"
    return csv_str


def tag_speeches(tagger: StanzaTagger, protocol: Protocol) -> List[dict]:

    speech_items = []
    speech_index = 1
    speech_texts = []

    for speech in protocol.speeches:

        text: str = speech.text.strip()

        if not text:
            continue

        speech_texts.append(text)
        document_name = f"{strip_extensions(protocol.name)}@{speech_index}"
        speech_items.append(
            {
                'speech_id': speech.speech_id,
                'speaker': speech.speaker or "Unknown",
                'speech_date': protocol.date,  # speech.speech_date or
                'speech_index': speech_index,
                'annotation': "",
                'document_name': document_name,
                'filename': f"{document_name}.csv",
                'num_tokens': 0,
                'num_words': 0,
            }
        )
        speech_index += 1

    documents: List[Document] = tagger.tag(speech_texts)
    for i, document in enumerate(documents):
        speech_items[i]['annotation'] = document_to_csv(document)
        speech_items[i]['num_tokens'] = document.num_tokens
        speech_items[i]['num_words'] = document.num_words

    return speech_items


def write_to_zip(output_filename: str, speech_items: dict) -> None:

    with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as fp:

        for item in speech_items:
            fp.writestr(item['filename'], item['annotation'])
            del item['annotation']

        document_index_str: str = pd.DataFrame(speech_items).to_csv(sep='\t', header=True)
        fp.writestr('document_index.csv', document_index_str)


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

    tagged_speeches = tag_speeches(tagger, protocol)

    write_to_zip(output_filename, tagged_speeches)
