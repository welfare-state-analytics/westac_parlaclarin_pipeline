import os
import pathlib
import zipfile
from typing import List

import pandas as pd
import stanza
from workflow.model import Protocol, dedent, dehyphen, tokenize
from workflow.model.utility.utils import strip_extensions

# from os import devnull

jj = os.path.join
nj = os.path.normpath

DEFAULT_STANZA_ROOT = nj("/data/sparv/models/stanza")

"""

NOTE! THIS CODE IS BASED ON https://spraakbanken.se/sparv-pipeline/modules/stanza/stanza.py

"""


STANZA_CONFIGS: dict = {
    "sv": {
        "resources_file": "resources.json",
        "lem_model": jj("lem", "sv_suc_lemmatizer.pt"),
        "pos_model": jj("pos", "full_sv_talbanken_tagger.pt"),
        "pretrain_pos_model": jj("pos", "full_sv_talbanken.pretrain.pt"),
        "dep_model": jj("dep", "sv_talbanken_parser.pt"),
        "pretrain_dep_model": jj("pos", "full_sv_talbanken.pretrain.pt"),
    }
}


class StanzaAnnotator:
    def __init__(self, model_root=DEFAULT_STANZA_ROOT, lang="sv"):
        config: dict = STANZA_CONFIGS[lang]
        self.nlp: stanza.Pipeline = stanza.Pipeline(
            lang=lang,
            processors="tokenize,lemma,pos",
            dir=model_root,
            pos_pretrain_path=jj(model_root, config["pretrain_pos_model"]),
            pos_model_path=jj(model_root, config["pos_model"]),
            lemma_model_path=jj(model_root, config["lem_model"]),
            tokenize_pretokenized=True,
            tokenize_no_ssplit=True,
            use_gpu=True,
        )

    def to_document(self, text: str) -> stanza.Document:
        """Annotates document using Stanza"""
        text: str = ' '.join(tokenize.tokenize(text))
        tagged_document: stanza.Document = self.nlp(text)
        return tagged_document

    def to_csv(self, text: str, sep='\t') -> str:
        """Annotates a text using Stanza and returns a TSV str"""
        tagged_document: stanza.Document = self.to_document(text)
        csv_str = self.document_to_csv(tagged_document, sep=sep)
        return csv_str

    @staticmethod
    def document_to_csv(tagged_document: stanza.Document, sep='\t') -> str:
        """Converts a stanza.Document to a TSV string"""
        csv_str = '\n'.join(f"{w.text}{sep}{w.lemma}{sep}{w.upos}{sep}{w.xpos}" for w in tagged_document.iter_words())
        return f"text{sep}lemma{sep}pos{sep}xpos\n{csv_str}"


def annotate_speeches(annotator: StanzaAnnotator, protocol: Protocol) -> List[dict]:

    speech_items = []
    speech_index = 1
    for speech in protocol.speeches:

        text: str = dehyphen(dedent(speech.text)).strip()

        if not text:
            continue

        speech_document: stanza.Document = annotator.to_document(text)

        speech_csv = annotator.document_to_csv(speech_document)
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
    annotator: StanzaAnnotator = None,
) -> None:

    os.makedirs(os.path.dirname(output_filename), exist_ok=True)

    pathlib.Path(output_filename).unlink(missing_ok=True)

    protocol: Protocol = Protocol.from_file(input_filename)

    if not protocol.has_speech_text():
        pathlib.Path(output_filename).touch(exist_ok=True)
        return

    speech_items = annotate_speeches(annotator, protocol)

    write_to_zip(output_filename, speech_items)
