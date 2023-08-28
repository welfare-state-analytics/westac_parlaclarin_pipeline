import os

import pytest
from pyriksprot import interface
from pyriksprot.corpus import parlaclarin
from pyriksprot_tagger.scripts import tag

from .utility import tag_test_data

jj = os.path.join


@pytest.mark.skipif(os.environ.get("RIKSPROT_DATA_FOLDER") is None, reason="no data")
def test_parse_xml_with_multiple_speaker_in_same_speech_error():
    # filename: str = jj(
    #     os.environ["RIKSPROT_DATA_FOLDER"], "riksdagen-corpus/corpus/protocols/199192/prot-199192--127.xml"
    # )

    filename: str = jj(
        os.environ["RIKSPROT_DATA_FOLDER"], "riksdagen-corpus/corpus/protocols/1911/prot-1911--ak--48.xml"
    )

    protocol: interface.Protocol = parlaclarin.parse.ProtocolMapper.parse(filename)

    assert protocol is not None


def test_tagit():
    folder: str = "tests/test_data/fakes"
    version: str = "v0.9.0"

    config_str: str = f"""
root_folder: .
source:
  folder: {folder}/{version}/parlaclarin
  tag: {version}
dehyphen:
  folder: {folder}/{version}/dehyphen_datadir
  tf_filename: {folder}/{version}/dehyphen_datadir/word-frequencies.pkl
tagger:
  module: pyriksprot_tagger.taggers.stanza_tagger
  stanza_datadir: /data/sparv/models/stanza
  preprocessors: "dedent,dehyphen,strip,pretokenize"
  lang: "sv"
  processors: "tokenize,lemma,pos"
  tokenize_pretokenized: true
  tokenize_no_ssplit: true
  use_gpu: true
  num_threads: 1
"""
    config_filename: str = "tests/output/tagit-config.yml"
    with open(config_filename, "w", encoding="utf8") as f:
        f.write(config_str)

    tag.tagit(
        config_filename=config_filename,
        source_folder=f"{folder}/{version}/parlaclarin",
        target_folder=f"tests/output/{version}/tagged_frames",
        force=True,
        recursive=True,
    )

    # FIXME: Add assertions, test that the output is correct as specfied in CSV files in folder "expected"


# @pytest.mark.skip(reason="done")
def test_tag_test_data():
    tag_test_data(folder="tests/test_data/source", version="v0.6.0")
