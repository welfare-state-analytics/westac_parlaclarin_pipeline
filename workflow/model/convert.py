from typing import Union

from jinja2 import Environment, PackageLoader, Template, select_autoescape, FileSystemLoader

from . import entities as model

# def create_jinja_env():
#     templateLoader = FileSystemLoader(searchpath="./")
#     templateEnv = Environment(loader=templateLoader)

jinja_env = Environment(
    loader=PackageLoader('resources', 'templates'),
    autoescape=select_autoescape(['html', 'xml']),
    trim_blocks=True,
    lstrip_blocks=True,
)


class ProtocolConverter:
    def __init__(self, template: Union[str, Template]):
        global jinja_env
        if isinstance(template, str):
            template = jinja_env.get_template(template)

        self.template: Template = template

    def convert(self, protocol: model.Protocol, filename: str) -> str:
        text: str = self.template.render(protocol=protocol, filename=filename)
        return text


def cli():
    pass


if __name__ == "__main__":
    cli
