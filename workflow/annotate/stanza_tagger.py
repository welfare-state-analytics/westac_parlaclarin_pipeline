import os
import pathlib
import zipfile
from typing import List

import pandas as pd
import stanza
from workflow.model import Protocol, dedent, dehyphen, tokenize
from workflow.model.utility.utils import strip_extensions


jj = os.path.join


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


class StanzaTagger:
    def __init__(self, model_root: str, lang: str="sv"):
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

