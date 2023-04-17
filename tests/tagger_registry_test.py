from os.path import abspath as aj

from pyriksprot import ITagger, TaggerRegistry
from pyriksprot_tagger.config import Config
from pyriksprot_tagger.taggers import StanzaTagger, StanzaTaggerFactory


def test_tagger_registry_get():
    config_filename: str = aj("./tests/test_data/test_config.yml")
    typed_config: Config = Config.load(source=config_filename)
    tagger: ITagger = TaggerRegistry.get(
        factory=StanzaTaggerFactory.factory(
            stanza_datadir=typed_config.stanza_dir,
            dehyphen_datadir=typed_config.dehyphen.folder,
            word_frequencies=typed_config.dehyphen.tf_filename,
            use_gpu=False,
        )
    )

    assert isinstance(tagger, StanzaTagger)

    tagger2: ITagger = TaggerRegistry.get(
        factory=StanzaTaggerFactory.factory(
            stanza_datadir=typed_config.stanza_dir,
            dehyphen_datadir=typed_config.dehyphen.folder,
            word_frequencies=typed_config.dehyphen.tf_filename,
            use_gpu=False,
        )
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
    tagger: ITagger = StanzaTaggerFactory.factory(
        stanza_datadir=typed_config.stanza_dir,
        dehyphen_datadir=typed_config.dehyphen.folder,
        word_frequencies=typed_config.dehyphen.tf_filename,
        use_gpu=False,
    ).create()

    assert tagger is not None
