from pyriksprot import ITagger

from workflow.taggers import StanzaTagger, TaggerRegistry
from os.path import abspath as aj
from workflow.config import Config, load_typed_config


def test_tagger_registry_get():
    config_filename: str = aj("./tests/test_data/test_config.yml")
    typed_config: Config = load_typed_config(config_filename)
    dehyphen_opts = dict(word_frequency_filename=typed_config.word_frequency.fullname, **typed_config.dehyphen.opts)
    tagger: ITagger = TaggerRegistry.get(
        tagger_cls=StanzaTagger,
        model=typed_config.stanza_dir,
        dehyphen_opts=dehyphen_opts,
        use_gpu=False,
    )
    assert isinstance(tagger, StanzaTagger)

    tagger2: ITagger = TaggerRegistry.get(
        tagger_cls=StanzaTagger,
        model=typed_config.stanza_dir,
        dehyphen_opts=dehyphen_opts,
        use_gpu=False,
    )

    assert tagger2 is tagger

def test_tagger():
    config_filename: str = aj("./workflow/config/config.yml")
    typed_config: Config = load_typed_config(config_filename)
    tagger: ITagger = TaggerRegistry.stanza(typed_config, disable_gpu=True)

    assert tagger is not None
