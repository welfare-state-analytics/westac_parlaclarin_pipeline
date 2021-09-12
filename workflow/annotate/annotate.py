import contextlib
import json
import os
import zipfile
from typing import List, Literal, Optional

from loguru import logger
from workflow.model.model import Utterance, Utterances
from workflow.model.utility.utils import strip_path_and_extension

from ..model import Protocol, parse
from ..model.utility import ensure_path, touch, unlink
from .interface import ITagger, TaggedDocument

CHECKSUM_FILENAME: str = 'sha1_checksum.txt'
METADATA_FILENAME: str = 'metadata.json'

StorageFormat = Literal['csv', 'json']

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


def store_protocol(
    output_filename: str, protocol: Protocol, checksum: str, storage_format: StorageFormat = 'json'
) -> None:
    """Store tagged protocol in `output_filename`, with metadata."""

    if output_filename.endswith("zip"):

        with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as fp:

            metadata: dict = dict(name=protocol.name, date=protocol.date, checksum=checksum)
            fp.writestr(METADATA_FILENAME, json.dumps(metadata, indent=4))

            if storage_format == 'csv':
                utterances_csv_str: str = protocol.to_csv()
                fp.writestr(f'{protocol.name}.csv', utterances_csv_str or "")

            elif storage_format == 'json':
                utterances_json_str: str = protocol.to_json()
                fp.writestr(f'{protocol.name}.json', utterances_json_str or "")

            # document_index: pd.DataFrame = (
            #     pd.DataFrame(speeches)
            #     .set_index('document_name', drop=False)
            #     .rename_axis('')
            #     .assign(document_id=range(0, len(speeches)))
            # )
            # fp.writestr('document_index.csv', document_index.to_csv(sep='\t', header=True))

    else:

        raise ValueError("Only Zip store currently implemented")


def load_metadata(filename: str) -> Optional[dict]:

    if not os.path.isfile(filename):
        return None

    with contextlib.suppress(Exception):

        with zipfile.ZipFile(filename, 'r') as fp:

            filenames: List[str] = [f.filename for f in fp.filelist]

            if METADATA_FILENAME not in filenames:
                return None

            json_str = fp.read(METADATA_FILENAME).decode('utf-8')

            return json.loads(json_str)


PROTOCOL_LOADERS: dict = dict(
    json=Utterances.from_json,
    csv=Utterances.from_csv,
)


def load_protocol(filename: str) -> Optional[Protocol]:

    metadata: dict = load_metadata(filename)

    if metadata is None:
        return None

    with zipfile.ZipFile(filename, 'r') as fp:

        basename: str = metadata['name']

        filenames: List[str] = [f.filename for f in fp.filelist]

        for ext in PROTOCOL_LOADERS:

            stored_filename: str = f"{basename}.{ext}"

            if not stored_filename in filenames:
                continue

            data_str: str = fp.read(stored_filename).decode('utf-8')
            utterances: List[Utterance] = PROTOCOL_LOADERS.get(ext)(data_str)

            protocol: Protocol = Protocol(utterances=utterances, **metadata)

            return protocol


def validate_checksum(filename: str, checksum: str) -> bool:
    metadata: dict = load_metadata(filename)
    if metadata is None:
        return False
    return checksum == metadata.get('checksum', 'oo')


def tag_protocol(tagger: ITagger, protocol: Protocol, preprocess=False) -> Protocol:

    texts = [u.text for u in protocol.utterances]

    documents: List[TaggedDocument] = tagger.tag(texts, preprocess=preprocess)

    for i, document in enumerate(documents):
        protocol.utterances[i].annotation = tagger.to_csv(document)
        protocol.utterances[i].num_tokens = document.get("num_tokens")
        protocol.utterances[i].num_words = document.get("num_words")

    return protocol


def tag_protocol_xml(
    input_filename: str,
    output_filename: str,
    tagger: ITagger,
    skip_size: int = 5,
    force: bool = False,
    storage_format: StorageFormat = 'json',
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

            protocol = tag_protocol(tagger, protocol=protocol)

            store_protocol(output_filename, protocol=protocol, checksum=checksum, storage_format=storage_format)

    except Exception:
        logger.error(f"FAILED: {input_filename}")
        unlink(output_filename)
        raise
