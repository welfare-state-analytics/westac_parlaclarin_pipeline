"""PoS tagging using Stanford's Stanza library.
NOTE! THIS CODE IS IN PART BASED ON https://github.com/spraakbanken/sparv-pipeline/blob/master/sparv/modules/stanza/stanza.py
"""

import os
from functools import reduce
from typing import Callable, List, Union

import stanza

from ..model.convert import pretokenize

jj = os.path.join


"""Follow Språkbanken Sparv's naming of model names and config keys."""
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

def document_to_csv(tagged_document: stanza.Document, sep='\t') -> str:
    """Converts a stanza.Document to a TSV string"""
    csv_str = '\n'.join(f"{w.text}{sep}{w.lemma}{sep}{w.upos}{sep}{w.xpos}" for w in tagged_document.iter_words())
    csv_str = f"text{sep}lemma{sep}pos{sep}xpos\n{csv_str}"
    return csv_str


class StanzaTagger:
    """Stanza PoS tagger wrapper"""

    def __init__(
        self,
        model_root: str,
        preprocessors: Callable[[str], str],
        lang: str = "sv",
        processors: str = "tokenize,lemma,pos",
        tokenize_pretokenized: bool = True,
        tokenize_no_ssplit: bool = True,
        use_gpu: bool = True,
    ):
        """Initialize stanza pipeline

        Args:
            model_root (str): where Språkbanken's Stanza models are stored
            preprocessors (Callable[[str], str]): Text transforms to do prior to tagging.
            lang (str, optional): Language (only 'sv' supported). Defaults to "sv".
            processors (str, optional): Stanza process steps. Defaults to "tokenize,lemma,pos".
            tokenize_pretokenized (bool, optional): If true, then already tokenized. Defaults to True.
            tokenize_no_ssplit (bool, optional): [description]. Defaults to True.
            use_gpu (bool, optional): If true, ten use GPU if exists. Defaults to True.
        """
        config: dict = STANZA_CONFIGS[lang]
        self.nlp: stanza.Pipeline = stanza.Pipeline(
            lang=lang,
            processors=processors,
            dir=model_root,
            pos_pretrain_path=jj(model_root, config["pretrain_pos_model"]),
            pos_model_path=jj(model_root, config["pos_model"]),
            lemma_model_path=jj(model_root, config["lem_model"]),
            tokenize_pretokenized=tokenize_pretokenized,
            tokenize_no_ssplit=tokenize_no_ssplit,
            use_gpu=use_gpu,
            verbose=False,
        )
        self.preprocessors: Callable[[str], str] = preprocessors or [pretokenize]

    def _preprocess(self, text: str) -> str:
        """Transform `text` with preprocessors."""
        text: str = reduce(lambda res, f: f(res), self.preprocessors, text)
        return text

    def tag(self, text: Union[str, List[str]]) -> List[stanza.Document]:
        """Tag text! Return stanza documents"""
        if isinstance(text, str):
            text = [text]

        if isinstance(text, list):

            if len(text) == 0:
                return []

            documents: List[stanza.Document] = [stanza.Document([], text=self._preprocess(d)) for d in text]

            tagged_documents: List[stanza.Document] = self.nlp(documents)

            if isinstance(tagged_documents, stanza.Document):
                tagged_documents = [tagged_documents]

            return tagged_documents

        return ValueError("invalid type")
