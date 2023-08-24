import os
from unittest.mock import MagicMock, patch

import pytest
from pyriksprot import configuration, interface
from pyriksprot.configuration import ConfigStore
from pyriksprot.corpus.parlaclarin import parse
from pyriksprot.workflows import tag
from pyriksprot_tagger import taggers
from pytest import fixture
from stanza import Document, Pipeline

nj = os.path.normpath
jj = os.path.join

MODEL_ROOT = "/data/sparv/models/stanza"

os.makedirs(jj("tests", "output"), exist_ok=True)

# pylint: disable=redefined-outer-name
if not os.path.isdir(MODEL_ROOT):
    pytest.skip(f"Skipping Stanza tests since model path {MODEL_ROOT} doesn't exist.", allow_module_level=True)


def dehyphen(text: str) -> str:
    return text


def configure_test_context():
    configuration.configure_context(
        "default",
        {
            'root_folder': 'tests/output/work_folder',
            'target_folder': 'tests/output/tagged_frames',
            'repository_folder': 'tests/output/work_folder/riksdagen-corpus',
            'repository_tag': 'v0.6.0',
            'tagger': {
                'module': 'pyriksprot_tagger.taggers.stanza_tagger',
                'stanza_datadir': 'tests/output/work_folder/sparv/models/stanza',
                'preprocessors': "dedent,dehyphen,strip,pretokenize",
                'lang': "sv",
                'processors': "tokenize,lemma,pos",
                'tokenize_pretokenized': True,
                'tokenize_no_ssplit': True,
                'use_gpu': False,
                'num_threads': 1,
            },
        },
    )


def test_registered_sparv_processor_variant_is_called():
    nlp = Pipeline(dir=MODEL_ROOT, lang='sv', processors={"tokenize": "default"}, package=None)
    x: Document = nlp("Jag heter Ove. Vad heter du?")
    assert isinstance(x, Document)

    with patch("pyriksprot_tagger.taggers.stanza_tagger.BetterSparvTokenizer.process", MagicMock(return_value="APA")):
        nlp = Pipeline(dir=MODEL_ROOT, lang='sv', processors={"tokenize": "sparv"}, package=None)
        assert nlp("Jag heter Ove. Vad heter du?") == "APA"

    with patch("pyriksprot_tagger.taggers.stanza_tagger.BetterSparvTokenizer.process", MagicMock(return_value="APA")):
        nlp = Pipeline(
            dir=MODEL_ROOT, lang='sv', processors={"tokenize": "sparv"}, package=None, tokenize_with_sparv=True
        )
        assert nlp("Jag heter Ove. Vad heter du?") == "APA"

    nlp = Pipeline(dir=MODEL_ROOT, lang='sv', processors="tokenize", package=None, tokenize_with_sparv=False)
    assert isinstance(x, Document)


def test_register_sparv_processor_variant():
    sentences_str: str = "Jag heter Ove. Vad heter du?"

    nlp = Pipeline(
        dir=MODEL_ROOT,
        lang='sv',
        processors={"tokenize": "default"},
        package=None,
    )

    doc: Document = nlp(sentences_str)
    assert len(doc.sentences) == 2

    nlp = Pipeline(dir=MODEL_ROOT, lang='sv', processors={"tokenize": "sparv"}, package=None, tokenize_no_ssplit=True)

    doc = nlp(sentences_str)
    assert len(doc.sentences) == 1

    nlp = Pipeline(dir=MODEL_ROOT, lang='sv', processors={"tokenize": "sparv"}, package=None, tokenize_no_ssplit=False)
    doc = nlp(sentences_str)
    assert len(doc.sentences) == 2


@fixture(scope="session")
def tagger() -> taggers.StanzaTagger:
    _tagger: taggers.StanzaTagger = taggers.StanzaTagger(
        stanza_datadir=MODEL_ROOT, preprocessors="dedent,dehyphen,strip,pretokenize", use_gpu=False
    )
    return _tagger


def test_stanza_annotator_to_document(tagger: taggers.StanzaTagger):
    text: str = "Detta är ett test!"

    configure_test_context()

    tagged_documents: list[tag.TaggedDocument] = tagger.tag(text, preprocess=True)

    assert len(tagged_documents) == 1

    assert tagged_documents[0]['token'] == ['Detta', 'är', 'ett', 'test', '!']
    assert tagged_documents[0]['lemma'] == ['detta', 'vara', 'en', 'test', '!']
    assert tagged_documents[0]['pos'] == ['PN', 'VB', 'DT', 'NN', 'MAD']


def test_stanza_tag(tagger: taggers.StanzaTagger):
    text: str = "Hej! Detta är ett test!"

    configure_test_context()

    tagged_documents: list[tag.TaggedDocument] = tagger.tag(text, preprocess=True)

    expected_documents = [
        {
            'lemma': ['hej', '!', 'detta', 'vara', 'en', 'test', '!'],
            'num_tokens': 7,
            'num_words': 7,
            'pos': ['IN', 'MID', 'PN', 'VB', 'DT', 'NN', 'MAD'],
            'token': ['Hej', '!', 'Detta', 'är', 'ett', 'test', '!'],
            'xpos': [
                'IN',
                'MID',
                'PN.NEU.SIN.DEF.SUB+OBJ',
                'VB.PRS.AKT',
                'DT.NEU.SIN.IND',
                'NN.NEU.SIN.IND.NOM',
                'MAD',
            ],
            # 'sentence_id': [0, 0, 0, 0, 0, 0, 0],
        }
    ]

    assert tagged_documents == expected_documents

FAKE_DOCUMENTS = [
    "Hej! Detta är en mening.",
    "Jag heter Ove. Vad heter du?",
    "Jag heter Adam.",
    "Ove är dum.",
]

EXPECTED_TAGGED_RESULT_FAKE_1958 = [
    [
        ('token', 'lemma', 'pos', 'xpos', 'sentence_id'),
        ('Hej', 'hej', 'IN', 'IN', 'FIRST_SENTENCE'),
        ('!', '!', 'MID', 'MID', 'FIRST_SENTENCE'),
        ('Detta', 'detta', 'PN', 'PN.NEU.SIN.DEF.SUB+OBJ', 'SECOND_SENTENCE'),
        ('är', 'vara', 'VB', 'VB.PRS.AKT', 'SECOND_SENTENCE'),
        ('en', 'en', 'DT', 'DT.UTR.SIN.IND', 'SECOND_SENTENCE'),
        ('mening', 'mening', 'NN', 'NN.UTR.SIN.IND.NOM', 'SECOND_SENTENCE'),
        ('.', '.', 'MAD', 'MAD', 'SECOND_SENTENCE'),
    ],
    [
        ('token', 'lemma', 'pos', 'xpos', 'sentence_id'),
        ('Jag', 'jag', 'PN', 'PN.UTR.SIN.DEF.SUB', 'FIRST_SENTENCE'),
        ('heter', 'heta', 'VB', 'VB.PRS.AKT', 'FIRST_SENTENCE'),
        ('Ove', 'Ove', 'PM', 'PM.NOM', 'FIRST_SENTENCE'),
        ('.', '.', 'MID', 'MID', 'FIRST_SENTENCE'),
        ('Vad', 'vad', 'HP', 'HP.NEU.SIN.IND', 'SECOND_SENTENCE'),
        ('heter', 'heta', 'VB', 'VB.PRS.AKT', 'SECOND_SENTENCE'),
        ('du', 'du', 'PN', 'PN.UTR.SIN.DEF.SUB', 'SECOND_SENTENCE'),
        ('?', '?', 'MAD', 'MAD', 'SECOND_SENTENCE'),
    ],
    [
        ('token', 'lemma', 'pos', 'xpos', 'sentence_id'),
        ('Jag', 'jag', 'PN', 'PN.UTR.SIN.DEF.SUB', 'FIRST_SENTENCE'),
        ('heter', 'heta', 'VB', 'VB.PRS.AKT', 'FIRST_SENTENCE'),
        ('Adam', 'Adam', 'PM', 'PM.NOM', 'FIRST_SENTENCE'),
        ('.', '.', 'MAD', 'MAD', 'FIRST_SENTENCE'),
    ],
    [
        ('token', 'lemma', 'pos', 'xpos', 'sentence_id'),
        ('Ove', 'Ove', 'PM', 'PM.NOM', 'FIRST_SENTENCE'),
        ('är', 'vara', 'VB', 'VB.PRS.AKT', 'FIRST_SENTENCE'),
        ('dum', 'dum', 'JJ', 'JJ.POS.UTR.SIN.IND.NOM', 'FIRST_SENTENCE'),
        ('.', '.', 'MAD', 'MAD', 'FIRST_SENTENCE'),
    ],
]

DEFAULT_TAGGER_OPTS: dict = {
    'lang': 'sv',
    'processors': 'tokenize,lemma,pos',
    'tokenize_pretokenized': False,
    'tokenize_no_ssplit': False,
    'use_gpu': True,
    'num_threads': None,
    'preprocessors': 'dedent,dehyphen,strip',
    'tokenize_with_sparv': True,
}


def test_stanza_tagger():
    tagger: taggers.StanzaTagger = taggers.StanzaTagger(
        lang='sv',
        processors='tokenize,lemma,pos',
        tokenize_no_ssplit=False,
        stanza_datadir=MODEL_ROOT,
        preprocessors="pretokenize",
        use_gpu=False,
        tokenize_with_sparv=False,
        tokenize_pretokenized=True,
    )
    documents: list[dict] = tagger.tag(FAKE_DOCUMENTS, preprocess=True)

    assert all(all(x == 0 for x in doc['sentence_id']) for doc in documents)

    # for i, document in enumerate(documents):
    #     protocol.utterances[i].annotation = tagger.to_csv(document)
    #     protocol.utterances[i].num_tokens = document.get("num_tokens")
    #     protocol.utterances[i].num_words = document.get("num_words")


def test_stanza_tag_protocol():
    ConfigStore.configure_context("default", DEFAULT_TAGGER_OPTS) #"tests/test_data/test_config.yml")

    tagger: taggers.StanzaTagger = taggers.StanzaTagger(
        lang='sv',
        processors='tokenize,lemma,pos',
        tokenize_no_ssplit=True,
        stanza_datadir=MODEL_ROOT,
        preprocessors="dedent,dehyphen,strip,pretokenize",
        use_gpu=False,
        tokenize_with_sparv=False,
        tokenize_pretokenized=True,
    )

    expected_output = ['\n'.join(['\t'.join(x[:-1]) for x in r]) for r in EXPECTED_TAGGED_RESULT_FAKE_1958]

    protocol: interface.Protocol = parse.ProtocolMapper.parse(jj("tests", "test_data", "fake", "prot-1958-fake.xml"))

    tag.tag_protocol(tagger, protocol, preprocess=True)

    assert [u.annotation for u in protocol.utterances] == expected_output


def test_stanza_tag_protocol_with_no_utterances(tagger: taggers.StanzaTagger):
    filename: str = jj("tests", "test_data", "fake", "prot-1980-fake-empty.xml")

    protocol: interface.Protocol = parse.ProtocolMapper.parse(filename)

    protocol = tag.tag_protocol(tagger, protocol)

    assert protocol is not None


def test_stanza_tag_protocol_xml(tagger: taggers.StanzaTagger):
    # tagger = Mock(spec=taggers.StanzaTagger, tag=lambda *_, **_: [])
    configure_test_context()
    input_filename: str = jj("tests", "test_data", "fake", "prot-1958-fake.xml")
    output_filename: str = jj("tests", "output", "prot-1958-fake.zip")

    tag.tag_protocol_xml(input_filename, output_filename, tagger)

    assert os.path.isfile(output_filename)


def register(registry: dict, key: str = None):
    if not isinstance(registry, dict):
        if not hasattr(registry, "registry"):
            registry.registry = {}
            registry = registry.registry

    def registrar(func):
        registry[key or func.__name__] = func
        return func

    return registrar
