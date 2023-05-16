from pyriksprot import ITagger, TaggerRegistry, configuration
from pyriksprot_tagger.taggers import StanzaTagger, StanzaTaggerFactory

config_data = """
root_folder: tests/output/work_folder
target_folder: tests/output/tagged_frames
repository_folder: tests/output/work_folder/riksdagen-corpus
repository_tag: v0.6.0
tagger:
  module: pyriksprot_tagger.taggers.stanza_tagger
  stanza_datadir: null
  preprocessors: "dedent,dehyphen,strip,pretokenize"
  lang: "sv"
  processors: "tokenize,lemma,pos"
  tokenize_pretokenized: true
  tokenize_no_ssplit: true
  use_gpu: false
  num_threads: 1
dehyphen:
    folder: .
    tf_filename: tests/test_data/word-frequencies.pkl
"""


def test_tagger_registry_get():
    config: configuration.Config = configuration.Config.load(source=config_data)

    tagger: ITagger = TaggerRegistry.get(
        factory=StanzaTaggerFactory.factory(
            stanza_datadir=config.get("tagger.stanza_datadir"),
            dehyphen_datadir=config.get("dehyphen:folder"),
            word_frequencies=config.get("dehyphen:tf_filename,tf_filename"),
            use_gpu=False,
        )
    )

    assert isinstance(tagger, StanzaTagger)

    tagger2: ITagger = TaggerRegistry.get(
        factory=StanzaTaggerFactory.factory(
            stanza_datadir=config.get("tagger.stanza_dir"),
            dehyphen_datadir=config.get("dehyphen:folder"),
            word_frequencies=config.get("dehyphen:tf_filename"),
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
tagger:
    module: pyriksprot_tagger.taggers.stanza_tagger
    stanza_datadir: ./tests/output/work_folder/sparv/models/stanza
dehyphen:
    folder: .
    tf_filename: tests/test_data/word-frequencies.pkl
"""


def test_tagger():
    config: configuration.Config = configuration.configure_context(context="default", source=SIMPLE_YAML_STR)

    tagger: ITagger = StanzaTaggerFactory.factory(
        stanza_datadir=config.get("tagger.stanza_datadir", mandatory=True),
        dehyphen_datadir=config.get("dehyphen:folder", mandatory=True),
        word_frequencies=config.get("dehyphen:tf_filename", mandatory=True),
        use_gpu=False,
    ).create()

    assert tagger is not None
