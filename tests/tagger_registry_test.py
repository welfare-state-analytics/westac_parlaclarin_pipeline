from os.path import abspath as aj

from pyriksprot import ITagger

from workflow.config import Config
from workflow.taggers import StanzaTagger, TaggerRegistry


def test_tagger_registry_get():
    config_filename: str = aj("./tests/test_data/test_config.yml")
    typed_config: Config = Config.load(source=config_filename)
    dehyphen_opts = dict(word_frequency_filename=typed_config.tf_opts.filename, **typed_config.dehyphen.opts)
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


SIMPLE_YAML_STR: str = """
data_folder: tests/output/work_folder
target_folder: tests/output/tagged_frames
repository_folder: tests/output/work_folder/riksdagen-corpus
repository_tag: v0.9.9
source_folder: /data/riksdagen-corpus/corpus/protocols
"""


def test_tagger():

    typed_config: Config = Config.load(source=SIMPLE_YAML_STR)
    tagger: ITagger = TaggerRegistry.stanza(typed_config, disable_gpu=True)

    assert tagger is not None
