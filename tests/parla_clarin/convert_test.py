import os
import sys

from workflow.model import convert
from workflow.model import entities as model

sys.path.append((lambda d: os.path.join(os.getcwd().split(d)[0], d))("parla_clarin_pipeline"))


def test_convert_to_xml():

    template_name: str = "speeches.xml.jinja"
    protocol: model.Protocol = model.Protocol.from_file("tests/test_data/test.xml")

    assert protocol is not None

    converter: convert.ProtocolConverter = convert.ProtocolConverter(template_name)

    result: str = converter.convert(protocol, "test.xml")

    expected = """<?xml version="1.0" encoding="UTF-8"?>
<protocol name="test" date="1958-01-01">
    <speech speaker="A" speech_id="i-1" speech_date="1958-01-01" speech_index="1">
a b c d
e?
f g h i.
j k l m
    </speech>
    <speech speaker="B" speech_id="i-3" speech_date="1958-01-01" speech_index="2">
a
f g h i.
j k l m
e?
f g h i.
j k l m
n
o p.
    </speech>
    <speech speaker="C" speech_id="i-6" speech_date="1958-01-01" speech_index="3">
a b
f g h i.
j k l m o
    </speech>
    <speech speaker="D" speech_id="i-7" speech_date="1958-01-01" speech_index="4">
a c
f g h i.
j k l m
a
f g h i.
j k l m
    </speech>
</protocol>"""
    assert result == expected
