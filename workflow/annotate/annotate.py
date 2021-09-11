import contextlib
import os
import zipfile
from typing import List, Optional

import pandas as pd
from loguru import logger
from workflow.model.utility.utils import strip_path_and_extension

from ..model import Protocol, Speech, parse
from ..model.utility import ensure_path, touch, unlink
from .interface import ITagger, TaggedDocument

CHECKSUM_FILENAME: str = 'sha1_checksum.txt'

# @deprecated
# def bulk_tag_protocols(tagger: ITagger, protocols: List[Protocol], skip_size: int = 5) -> List[List[dict]]:

#     speech_items: List[Dict[str, Any]] = []
#     protocol_refs = {}

#     for protocol in protocols:
#         idx = len(speech_items)
#         speech_items.extend(protocol.to_dict(skip_size=skip_size))
#         protocol_refs[protocol.name] = (idx, len(speech_items) - idx)

#     speech_items: List[Dict[str, Any]] = tag_speech_items(tagger, speech_items)

#     protocol_speech_items = []
#     for protocol in protocols:
#         idx, n_count = protocol_refs[protocol.name]
#         protocol_speech_items.append(speech_items[idx : idx + n_count])

#     return protocol_speech_items


def store_tagged_speeches(output_filename: str, speeches: List[Speech], checksum: str) -> None:
    """Store tagged speeches in `output_filename`, and create and store index."""

    if output_filename.endswith("zip"):

        with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as fp:

            """Store SHA-1"""
            if checksum is not None:
                fp.writestr(CHECKSUM_FILENAME, checksum)

            """Store each speech as a CSV"""
            for speech in speeches:
                fp.writestr(speech.filename, speech.annotation or "")

            """Create document index and store as a CSV"""
            document_index: pd.DataFrame = (
                pd.DataFrame(speeches)
                .set_index('document_name', drop=False)
                .rename_axis('')
                .assign(document_id=range(0, len(speeches)))
            )

            fp.writestr('document_index.csv', document_index.to_csv(sep='\t', header=True))

    else:

        raise ValueError("Only Zip store currently implemented")


def load_checksum(filename: str) -> Optional[str]:
    checksum: Optional[str] = None
    if not os.path.isfile(filename):
        return None
    with contextlib.suppress(Exception):
        with zipfile.ZipFile(filename, 'r') as fp:
            checksum = fp.read(CHECKSUM_FILENAME).decode('utf-8')
    return checksum


def validate_checksum(filename: str, checksum: str) -> bool:
    stored_checksum: str = load_checksum(filename)
    if stored_checksum is None:
        return False
    return checksum == stored_checksum


def tag_speeches(tagger: ITagger, speeches: List[Speech], preprocess=False) -> List[Speech]:

    texts = [speech.text for speech in speeches]

    documents: List[TaggedDocument] = tagger.tag(texts, preprocess=preprocess)

    for i, document in enumerate(documents):
        speeches[i].annotation = tagger.to_csv(document)
        speeches[i].num_tokens = document.get("num_tokens")
        speeches[i].num_words = document.get("num_words")

    return speeches


def tag_protocol_xml(
    input_filename: str, output_filename: str, tagger: ITagger, skip_size: int = 5, force: bool = False
) -> None:
    """Annotate XML protocol `input_filename` to `output_filename`.

    Args:
        input_filename (str, optional): Defaults to None.
        output_filename (str, optional): Defaults to None.
        tagger (StanzaTagger, optional): Defaults to None.
    """

    try:

        ensure_path(output_filename)

        protocol: Protocol = parse.ProtocolMapper.to_protocol(input_filename, skip_size=skip_size)

        if not protocol.has_text():

            unlink(output_filename)
            touch(output_filename)

            return

        protocol.preprocess(tagger.preprocess)

        checksum: str = protocol.checksum()

        if not force and validate_checksum(output_filename, checksum):

            logger.info(f"SKIPPING {strip_path_and_extension(input_filename)} (checksum validates OK)")

            touch(output_filename)

        else:

            unlink(output_filename)

            speeches: List[Speech] = protocol.to_speeches(merge_strategy='n')
            tagged_speeches = tag_speeches(tagger, speeches)

            store_tagged_speeches(output_filename, tagged_speeches, checksum=checksum)

    except Exception:
        logger.error(f"FAILED: {input_filename}")
        unlink(output_filename)
        raise
