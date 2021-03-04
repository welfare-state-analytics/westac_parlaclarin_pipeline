import os
import sys

sys.path.append(
    (lambda d: os.path.join(os.getcwd().split(d)[0], d))("parla_clarin_pipeline")
)


from typing import Any

import untangle

from workflow.model import convert
from workflow.model import entities as model


def hasattr_path(data: Any, path: str) -> bool:
    """Tests if attrib string in dot notation is present in data."""
    attribs = path.split(".")
    for attrib in attribs:
        if not hasattr(data, attrib):
            return False
        data = getattr(data, attrib)

    return True


def test_parse_xml():

    data = untangle.parse("tests/test_data/test.xml")

    assert hasattr_path(data, "teiCorpus.TEI.text.body.div.u"), "No u-tags in XML"

    div = data.teiCorpus.TEI.text.body.div
    assert len(div.u) == 8, "Wrong length"

    assert [div.u[i]["xml:id"] for i in range(0, 8)] == [
        f"i-{i+1}" for i in range(0, 8)
    ]


def test_speeches_when_merged_are_as_expected():

    data = untangle.parse("tests/test_data/test.xml")

    protocol = model.Protocol(data)

    assert len(protocol.speeches) == 4
    assert [len(s.segments) for s in protocol.speeches] == [2, 3, 1, 2]

    expected_paragraphs = [
        ["a b c d ", "e?\nf g h i.\nj k l m"],
        ["a\nf g h i.\nj k l m", "e?\nf g h i.\nj k l m", "n\no p."],
        ["a b\nf g h i.\nj k l m o"],
        ["a c\nf g h i.\nj k l m", "a\nf g h i.\nj k l m"],
    ]
    assert expected_paragraphs == [s.paragraphs for s in protocol.speeches]

    expected_segments = [
        [["a b c d "], ["e?", "f g h i.", "j k l m"]],
        [["a", "f g h i.", "j k l m"], ["e?", "f g h i.", "j k l m"], ["n", "o p."]],
        [["a b", "f g h i.", "j k l m o"]],
        [["a c", "f g h i.", "j k l m"], ["a", "f g h i.", "j k l m"]],
    ]
    assert expected_segments == [s.segments for s in protocol.speeches]

    assert [s.speech_id for s in protocol.speeches] == ["i-1", "i-3", "i-6", "i-7"]
    assert [s.speaker for s in protocol.speeches] == ["A", "B", "C", "D"]


def test_convert_to_xml():

    template_name: str = "to_xml_speeches.jinja"
    protocol: model.Protocol = model.Protocol.from_file("tests/test_data/test.xml")

    assert protocol is not None

    converter: convert.ProtocolConverter = convert.ProtocolConverter(template_name)

    result: str = converter.convert(protocol, "test.xml")

    # TODO: Ta bort extra mellanslag
    # TODO: Använda CData???
    expected = """
<?xml version="1.0" encoding="UTF-8"?>
<protocol xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" filename="test.xml">

    <speech speaker="A" speech_id="i-1" >

        <paragraph>
            a b c d
        </paragraph>

        <paragraph>
            e?
f g h i.
j k l m
        </paragraph>

    </speech>

    <speech speaker="B" speech_id="i-3" >

        <paragraph>
            a
f g h i.
j k l m
        </paragraph>

        <paragraph>
            e?
f g h i.
j k l m
        </paragraph>

        <paragraph>
            n
o p.
        </paragraph>

    </speech>

    <speech speaker="C" speech_id="i-6" >

        <paragraph>
            a b
f g h i.
j k l m o
        </paragraph>

    </speech>

    <speech speaker="D" speech_id="i-7" >

        <paragraph>
            a c
f g h i.
j k l m
        </paragraph>

        <paragraph>
            a
f g h i.
j k l m
        </paragraph>

    </speech>

</protocol>
"""
    assert result == expected
