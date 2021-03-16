import os
import textwrap
from typing import Union

from click import echo
from jinja2 import Environment, PackageLoader, Template, Undefined, select_autoescape
from workflow.model.dehyphen.swe_dehyphen import get_dehyphenator
from workflow.model.utility import strip_paths

from . import entities as model


def dedent(value: str) -> str:
    if isinstance(value, Undefined):
        raise ValueError("dedent: jinja2.Undefined value string encountered")
    return textwrap.dedent(value) if value is not None else ""


def dehyphen(value: str) -> str:
    dehyphenated_text = get_dehyphenator().dehyphenator.dehyphen_text(value)
    return dehyphenated_text


jinja_env = Environment(
    loader=PackageLoader('resources', 'templates'),
    autoescape=select_autoescape(['html', 'xml']),
    trim_blocks=True,
    lstrip_blocks=True,
)
jinja_env.filters['dedent'] = dedent
jinja_env.filters['dehyphen'] = dehyphen


class ProtocolConverter:
    def __init__(self, template: Union[str, Template]):

        global jinja_env

        if not template.endswith(".jinja"):
            template += ".jinja"

        if isinstance(template, str):
            template = jinja_env.get_template(template)

        self.template: Template = template

    def convert(self, protocol: model.Protocol, filename: str) -> str:
        text: str = self.template.render(protocol=protocol, filename=filename)
        return text


def convert_protocol(
    input_filename: str = None,
    output_filename: str = None,
    template_name: str = None,
):
    protocol: model.Protocol = model.Protocol.from_file(input_filename)
    converter: ProtocolConverter = ProtocolConverter(template_name)
    content: str = converter.convert(protocol, strip_paths(input_filename))

    if output_filename is not None:
        os.makedirs(os.path.dirname(output_filename), exist_ok=True)
        with open(output_filename, "w") as fp:
            fp.write(content)
    else:
        echo(content, nl=False, err=False)
