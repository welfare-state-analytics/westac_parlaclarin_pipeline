import os
from functools import reduce
from typing import Callable, List, Union

import stanza

from ..model.convert import pretokenize

jj = os.path.join


"""

NOTE! THIS CODE IS BASED ON https://spraakbanken.se/sparv-pipeline/modules/stanza/stanza.py

"""

StanzaDocument = stanza.Document

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
    def __init__(
        self,
        model_root: str,
        preprocessors: Callable[[str], str],
        lang: str = "sv",
        processors="tokenize,lemma,pos",
        tokenize_pretokenized=True,
        tokenize_no_ssplit=True,
        use_gpu=True,
    ):
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
        self.preprocessors = preprocessors or [pretokenize]

    def preprocess(self, text: str) -> str:
        text: str = reduce(lambda res, f: f(res), self.preprocessors, text)
        return text

    def tag(self, text: Union[str, List[str]]) -> List[StanzaDocument]:

        if isinstance(text, str):
            text = [text]

        if isinstance(text, list):

            if len(text) == 0:
                return []

            documents: List[StanzaDocument] = [StanzaDocument([], text=self.preprocess(d)) for d in text]

            tagged_documents: List[StanzaDocument] = self.nlp(documents)

            if isinstance(tagged_documents, StanzaDocument):
                tagged_documents = [tagged_documents]

            return tagged_documents

        return ValueError("invalid type")
