from typing import Mapping, Type

from loguru import logger
from pyriksprot import ITagger, SwedishDehyphenatorService, dedent, pretokenize

from ..config import Config

# from .spacy2 import SpacyTagger
from .stanza import StanzaTagger

# pylint: disable=unused-argument


class TaggerRegistry:

    instances: Mapping[Type[ITagger], ITagger] = {}

    @staticmethod
    def get(tagger_cls, model: str, dehyphen_opts: dict, use_gpu: bool = True, **kwargs) -> ITagger:

        if tagger_cls not in TaggerRegistry.instances:

            preprocessors = [
                dedent,
                SwedishDehyphenatorService.create_dehypen(**dehyphen_opts),
                str.strip,
                pretokenize,
            ]

            if tagger_cls is StanzaTagger:
                logger.info("creating Stanza tagger...")
                TaggerRegistry.instances[tagger_cls] = StanzaTagger(
                    model=model,
                    preprocessors=preprocessors,
                    use_gpu=use_gpu,
                )
                logger.info("Stanza tagger created.")

            # if tagger_cls is SpacyTagger:
            #     TaggerRegistry.instances[tagger_cls] = SpacyTagger(preprocessors=preprocessors, **kwargs)

        return TaggerRegistry.instances[tagger_cls]

    @staticmethod
    def stanza(cfg: Config, disable_gpu: bool) -> ITagger:
        """Get tagger from registry."""
        return TaggerRegistry.get(
            tagger_cls=StanzaTagger,
            model=cfg.stanza_dir,
            dehyphen_opts=dict(word_frequency_filename=cfg.word_frequency.fullname, **cfg.dehyphen.opts),
            use_gpu=not disable_gpu,
        )
