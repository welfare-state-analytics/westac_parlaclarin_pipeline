# Parla-Clarin Workflow

## Development setup

## Development install

Create a development install using hacky `pip install -e .`:

```bash
make development_install
```

For VS Code an alternative is to add `PYTHONPATH=./:$PYTHONPATH` to `.env` and configure a `launch.json` entry:

```
    {
        "name": "Python: pytest",
        "type": "python",
        "request": "launch",
        "module": "pytest",
        "cwd": "${workspaceRoot}",
        "env": {
            "PYTHONPATH": "${workspaceRoot}"
        },
        "envFile": "${workspaceRoot}/.env",
        "console": "integratedTerminal"
    }
```