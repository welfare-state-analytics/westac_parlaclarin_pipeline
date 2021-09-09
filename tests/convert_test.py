from workflow.model import convert, parse


def test_convert_to_xml():

    template_name: str = "speeches.xml.jinja"
    protocol: parse.Protocol = parse.Protocol.from_file("tests/test_data/fake/prot-1958-fake.xml")

    assert protocol is not None

    converter: convert.ProtocolConverter = convert.ProtocolConverter(template_name)

    result: str = converter.convert(protocol, "prot-200203--18.xml")

    expected = """<?xml version="1.0" encoding="UTF-8"?>
<protocol name="prot-1958-fake" date="1958">
    <speech speaker="A" speech_id="i-1" speech_date="1958" speech_index="1">
Hej! Detta är en mening.
Jag heter Ove.
Vad heter du?
    </speech>
    <speech speaker="B" speech_id="i-3" speech_date="1958" speech_index="2">
Jag heter Adam.
Ove är dum.
    </speech>
</protocol>"""

    assert result == expected
