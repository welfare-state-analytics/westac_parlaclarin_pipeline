from typing import Union

from jinja2 import Environment,  PackageLoader, Template, select_autoescape

from . import entities as model


jinja_env = Environment(
    loader=PackageLoader('resources', 'templates'),
    autoescape=select_autoescape(['html', 'xml']),
    trim_blocks=True,
    lstrip_blocks=True,
)


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
