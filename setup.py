# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['makeline',
 'resources',
 'resources.profile',
 'resources.templates',
 'scripts',
 'workflow',
 'workflow.config',
 'workflow.model',
 'workflow.model.dehyphen',
 'workflow.model.deprecated',
 'workflow.model.utility',
 'workflow.rules',
 'workflow.rules.xslt_rules']

package_data = \
{'': ['*'], 'resources': ['xslt/*'], 'workflow.rules': ['archive/*']}

install_requires = \
['Jinja2>=2.11.3,<3.0.0',
 'click>=7.1.2,<8.0.0',
 'dehyphen>=0.3.4,<0.4.0',
 'snakefmt>=0.3.1,<0.4.0',
 'snakemake==5.26.1',
 'sparv-pipeline>=4.0.0,<5.0.0',
 'torch>=1.8.0,<2.0.0',
 'transformers>=4.3.3,<5.0.0',
 'untangle>=1.1.1,<2.0.0',
 'xmltodict>=0.12.0,<0.13.0']

entry_points = \
{'console_scripts': ['parla_transform = scripts.parla_transform:main']}

setup_kwargs = {
    'name': 'westac-parlaclarin-pipeline',
    'version': '2021.3.1',
    'description': 'Pipeline that transforms Parla-Clarin XML files',
    'long_description': '# Parla-Clarin Workflow\n\n## Development setup\n\n## Development install\n\nCreate a development install using hacky `pip install -e .`:\n\n```bash\nmake development_install\n```\n\nFor VS Code an alternative is to add `PYTHONPATH=./:$PYTHONPATH` to `.env` and configure a `launch.json` entry:\n\n```\n    {\n        "name": "Python: pytest",\n        "type": "python",\n        "request": "launch",\n        "module": "pytest",\n        "cwd": "${workspaceRoot}",\n        "env": {\n            "PYTHONPATH": "${workspaceRoot}"\n        },\n        "envFile": "${workspaceRoot}/.env",\n        "console": "integratedTerminal"\n    }\n```',
    'author': 'Roger Mähler',
    'author_email': 'roger.mahler@hotmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://westac.se',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '==3.8.5',
}


setup(**setup_kwargs)