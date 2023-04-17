from __future__ import annotations

import os
from os.path import isdir
from typing import Callable, List, Union

import stanza
from loguru import logger
from pyriksprot import ITagger, ITaggerFactory, SwedishDehyphenator, TaggedDocument, pretokenize

from ..config import Config
from ..utility import create_text_preprocessors

"""PoS tagging using Stanford's Stanza library.
NOTE! THIS CODE IS IN PART BASED ON https://github.com/spraakbanken/sparv-pipeline/blob/master/sparv/modules/stanza/stanza.py

Fix Windows CUDA TDR error:

https://www.pugetsystems.com/labs/hpc/Working-around-TDR-in-Windows-for-a-better-GPU-computing-experience-777/

"""


jj = os.path.join

# pylint: disable=too-many-arguments

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


class StanzaTagger(ITagger):
    """Stanza PoS tagger wrapper"""

    def __init__(
        self,
        stanza_datadir: str,
        preprocessors: Callable[[str], str],
        lang: str = "sv",
        processors: str = "tokenize,lemma,pos",
        tokenize_pretokenized: bool = True,
        tokenize_no_ssplit: bool = True,
        use_gpu: bool = True,
        num_threads: int = None,
    ):
        super().__init__(preprocessors=preprocessors or [pretokenize])

        """Initialize stanza pipeline

        Args:
            model_root (str): where Språkbanken's Stanza models are stored
            preprocessors (Callable[[str], str]): Text transforms to do prior to tagging.
            lang (str, optional): Language (only 'sv' supported). Defaults to "sv".
            processors (str, optional): Stanza process steps. Defaults to "tokenize,lemma,pos".
            tokenize_pretokenized (bool, optional): If true, then already tokenized. Defaults to True.
            tokenize_no_ssplit (bool, optional): [description]. Defaults to True.
            use_gpu (bool, optional): If true, use GPU if exists. Defaults to True.
        """
        stanza_datadir = stanza_datadir or os.environ.get("STANZA_DATADIR")

        logger.info(f"stanza: processors={processors} use_gpu={use_gpu}")
        config: dict = STANZA_CONFIGS[lang]

        if isinstance(num_threads, (int, str)):
            os.environ['OMP_NUM_THREADS'] = str(num_threads)

        if not isdir(stanza_datadir):
            raise FileNotFoundError("STANZA_DATADIR not set to a valid path")

        self.nlp: stanza.Pipeline = stanza.Pipeline(
            lang=lang,
            processors=processors,
            dir=stanza_datadir,
            pos_pretrain_path=jj(stanza_datadir, config["pretrain_pos_model"]),
            pos_model_path=jj(stanza_datadir, config["pos_model"]),
            lemma_model_path=jj(stanza_datadir, config["lem_model"]),
            tokenize_pretokenized=tokenize_pretokenized,
            tokenize_no_ssplit=tokenize_no_ssplit,
            use_gpu=use_gpu,
            verbose=False,
        )

    def _tag(self, text: Union[str, List[str]]) -> List[TaggedDocument]:
        """Tag text. Return dict if lists."""

        documents: List[stanza.Document] = [stanza.Document([], text=d) for d in text]

        tagged_documents: List[stanza.Document] = self.nlp(documents)

        if isinstance(tagged_documents, stanza.Document):
            tagged_documents = [tagged_documents]

        return [self._to_dict(d) for d in tagged_documents]

    def _to_dict(self, tagged_document: stanza.Document) -> TaggedDocument:
        """Extract tokens from tagged document. Return dict of list."""

        tokens, lemmas, pos, xpos = [], [], [], []
        # FIXME: Iterate tokens instead???
        for w in tagged_document.iter_words():
            tokens.append(w.text)
            lemmas.append(w.lemma or w.text.lower())
            pos.append(w.upos)
            xpos.append(w.xpos)

        return dict(
            token=tokens,
            lemma=lemmas,
            pos=pos,
            xpos=xpos,
            num_tokens=tagged_document.num_tokens,
            num_words=tagged_document.num_words,
        )

    # @staticmethod
    # def to_csv(tagged_document: TaggedDocument, sep='\t') -> str:
    #     """Converts a stanza.Document to a TSV string"""

    #     csv_str = '\n'.join(f"{w.text}{sep}{w.lemma}{sep}{w.upos}{sep}{w.xpos}" for w in tagged_document.iter_words())
    #     csv_str = f"text{sep}lemma{sep}pos{sep}xpos\n{csv_str}"
    #     return csv_str


class StanzaTaggerFactory(ITaggerFactory):

    identifier: str = "stanza_swedish"

    def __init__(self, **opts) -> ITagger:
        self.opts = opts

    @staticmethod
    def factory(
        stanza_datadir: str = None,
        preprocessors: str = "dedent,dehyphen,strip,pretokenize",
        lang: str = "sv",
        processors: str = "tokenize,lemma,pos",
        tokenize_pretokenized: bool = True,
        tokenize_no_ssplit: bool = True,
        use_gpu: bool = True,
        num_threads: int = None,
        dehyphen_datadir: str = None,
        word_frequencies: str | dict = None,
    ) -> "StanzaTaggerFactory":
        """Typed abstract factory"""
        return StanzaTaggerFactory(
            stanza_datadir=stanza_datadir,
            preprocessors=preprocessors,
            lang=lang,
            processors=processors,
            tokenize_pretokenized=tokenize_pretokenized,
            tokenize_no_ssplit=tokenize_no_ssplit,
            use_gpu=use_gpu,
            num_threads=num_threads,
            dehyphen_datadir=dehyphen_datadir,
            word_frequencies=word_frequencies,
        )

    def create(self) -> ITagger:
        tagger: StanzaTagger = StanzaTagger(
            stanza_datadir=self.opts.get("stanza_datadir"),
            preprocessors=create_text_preprocessors(
                pipeline="dedent,dehyphen,strip,pretokenize",
                fxs_tasks={
                    'dehyphen': SwedishDehyphenator.create_dehypen(
                        data_folder=self.opts.get("dehyphen_datadir"),
                        word_frequencies=self.opts.get("word_frequencies"),
                    )
                },
            ),
            use_gpu=self.opts.get("use_gpu", True),
            num_threads=self.opts.get("num_threads", 2),
        )

        return tagger


def tagger_factory(config: Config) -> ITaggerFactory:
    tagger_opts: dict = {
        'dehyphen_datadir': config.dehyphen.folder,
        'stanza_datadir': config.stanza_dir,
        'word_frequencies': config.dehyphen.tf_filename,
        'preprocessors': "dedent,dehyphen,strip,pretokenize",
        'lang': "sv",
        'processors': "tokenize,lemma,pos",
        'tokenize_pretokenized': True,
        'tokenize_no_ssplit': True,
        'use_gpu': True,
        'num_threads': None,
    } | config.tagger_opts

    return StanzaTaggerFactory.factory(**tagger_opts)
