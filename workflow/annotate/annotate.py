import zipfile
from typing import Any, Dict, List

import pandas as pd
import stanza

from ..model.entities import Protocol
from ..model.utility import ensure_path, touch, unlink
from .stanza import StanzaTagger


def tag_protocol(tagger: StanzaTagger, protocol: Protocol, skip_size: int = 5) -> List[dict]:
    """Tag protocol using `tagger`.

    Args:
        tagger (StanzaTagger): Stanza pipeline wrapper
        protocol (Protocol): ParlaClarin XML protocol
        skip_size (int, optional): Skip text less then size. Defaults to 5.

    Returns:
        List[dict]: [description]
    """
    speech_items: List[Dict[str, Any]] = protocol.to_dict(skip_size=skip_size)
    speech_texts = [item['text'] for item in speech_items]
    documents: List[stanza.Document] = tagger.tag(speech_texts)
    for i, document in enumerate(documents):
        speech_items[i].update(
            annotation=tagger.to_csv(document),
            num_tokens=document.num_tokens,
            num_words=document.num_words,
        )

    return speech_items


def _store_tagged_protocol(output_filename: str, speech_items: List[dict]) -> None:
    """Store tagged speeches in `output_filename`, and create and store index."""

    if output_filename.endswith("zip"):

        with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as fp:

            """Store each speech as a CSV"""
            for item in speech_items:
                item['filename'] = f"{item['document_name']}.csv"
                fp.writestr(item['filename'], (item['annotation'] or ""))

            """Create document index and store as a CSV"""
            for item in speech_items:
                del item['annotation']
                del item['text']

            document_index: pd.DataFrame = (
                pd.DataFrame(speech_items)
                .set_index('document_name', drop=False)
                .rename_axis('')
                .assign(document_id=range(0, len(speech_items)))
            )

            fp.writestr('document_index.csv', document_index.to_csv(sep='\t', header=True))

    else:

        raise ValueError("Only Zip store currently implemented")


def tag_protocol_xml(input_filename: str, output_filename: str, tagger: StanzaTagger) -> None:
    """Annotate XML protocol `input_filename` to `output_filename`.

    Args:
        input_filename (str, optional): Defaults to None.
        output_filename (str, optional): Defaults to None.
        tagger (StanzaTagger, optional): Defaults to None.
    """

    ensure_path(output_filename)
    unlink(output_filename)

    protocol: Protocol = Protocol.from_file(input_filename)

    if protocol.has_speech_text():

        tagged_speeches = tag_protocol(tagger, protocol)

        _store_tagged_protocol(output_filename, tagged_speeches)

    else:

        touch(output_filename)
