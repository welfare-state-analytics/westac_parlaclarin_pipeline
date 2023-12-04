# Riksdagens Protokoll Part-Of-Speech Tagging

This package implements part-of-speech tagging of `Riksdagens Protokoll` (Parla-CLARIN)[https://clarin-eric.github.io/parla-clarin/] files.

## Prerequisites

 - The workflow makes use of `Gnu make`, `git`, `pyenv` and `poetry`.
 - Latest version of [welfare-state-analytics/pyriksprot](#install-pyriksprot).
 - Latest version of [welfare-state-analytics/pyriksprot_tagger](#install-pyriksprot-tagger).
 - NLP models for [Sparv and Stanza]((#install-sparv-and-stanza-models)) installed.
 - A local copy of [riksdagen-corpus](#setup-a-local-copy-of-riksdagen-corpus-github-repository) Github repository.
 
## Tagging Workflow

 1. Update `pyriksprot-tagger` [configuration]([#update-configuration) file (.env).
 1. Update [riksdagen-corpus](#setup-a-local-copy-of-riksdagen-corpus-github-repository) repository.
 1. Run the `tag.sh` script:
    ```bash
    PYTHONPATH=. nohup ./tag.sh --target-folder /path/to/output/data > tag-it.version.log &
    ```
    You can also execute a predefined make recepi:
    ```bash
    make tag-it
    ```
If you run `tag.sh` without parameters then the values found in `.env` will be used. You can also specify
parameters as command line options:

```man
usage: ./tag.sh [--data-folder folder] [--source-pattern pattern] --target-folder folder --tag tag [--force] [--update] [--max-procs n]]
Creates new database using source as template. Source defaults to production.

   --data-folder             source root folder
   --source-pattern          source folder pattern
   --target-folder           target folder
   --tag                     source corpus tag
   --force                   drop target if exists
   --update                  update target if exists
   --max-procs               max number of parallel jobs
```

Note that `tag.sh` will raise an error if the checkout tag in the Git repository and tag specified in .env (or as a parameter) mismatch.

## Metadata Workflow

This workflow processes the corpus metadata and generates an Sqlite relational database. This database is used by the Westac Notebooks when filtering and pivoting data based on speaker, party etc. Use [welfare-state-analytics/pyriksprot](https://github.com/welfare-state-analytics/pyriksprot) to create or update the metadata:

 - Update `pyriksprot/.env` and set current tag.
 - Run the `make metadata` to create a metadata database for current tag:

### Detailed workflow

Due to potentiallyy breaking changes in the metadata we need to find differences between the new and old version of the metadata. If new fields or coded values have been added or change, or any other breaking change has been made then most likely the scripts that processes the metadata needs to be updated. Data updates are made both using SQL scripts and Python scripts.

1. Identify breaking changes.
   - Download previous and current metadata in two seperate folders:
      ```
      metadata2db download v0.9.0 ./tmp/metadata/v0.9.0
      metadata2db download v0.10.0 ./tmp/metadata/v0.10.0
      ```
   > 💡 Alt: `python pyriksprot/scripts/metadata2db.py download v0.10.0 ./tmp/metadata/v0.10.0`

   >💡 Use [moshfeu.compare-folders](https://marketplace.visualstudio.com/items?itemName=moshfeu.compare-folders) to compare folders in vscode.
   - If you find structural differences than you need to file an issue and request the system to be updated to deal with the changes. Module `pyriksprot.sql` contains SQL scripts for metadata schema and (some) updates. Furthermore, some schema changes need to be handled in the `pyriksprot.module` module (e.g. `pyriksprot.module.config`). Changes may of course also affect the `penelope` corpus pipeline.
2. Create a metadata database using [welfare-state-analytics/pyriksprot](https://github.com/welfare-state-analytics/pyriksprot) for given tag:
    - Update `pyriksprot/.env` (e.g. tag)
    - Run the `metadata` recipe:
        ```bash
        make metadata
        ```

## Speech Corpus Workflow

 2. Create a default speech corpus using [welfare-state-analytics/pyriksprot_tagger](https://github.com/welfare-state-analytics/pyriksprot) for given tag:
    - Run te recipi `extract-speeches-to-feather`:
        ```bash
        make extract-speeches-to-feather
        ```

See appendix below if you instead want to use `snakemake` for updating repository and tagging,

## Install **pyriksprot** tagger

Easiest way is to clone the GitHub repository:

```bash
cd /path/to/any/folder
git clone git@github.com:welfare-state-analytics/pyriksprot_tagger
cd pyriksprot_tagger
pyenv local 3.11.3
poetry shell
pip install torch
poetry install
```

You can also [install the tagger](#install-pyriksprot-tagger-from-pypi) in an isolated Python virtual environment. This method requires you to manually download certain scripts depending on your specific workflow.

## Install Sparv and Stanza models

Use `stanza-models.sh` script to download Stanza files. Note that the target folder specified in the script must be the same as the folder specified by the STANZA_DATADIR environment variable (in .env).

Optional: Use `penelope/scripts/install-spacy-models.sh` to install relevant SpaCy models.


## Update configuration

Update or create dotenv (.env) in the `pyriksprot_tagger` folder with the following variable definitions:

| Environment variable    | Description                                                     |
| ----------------------- | --------------------------------------------------------------- |
| RIKSPROT_DATA_FOLDER    | Parent folder (location) of Riksdagens corpus data folder       |
| RIKSPROT_REPOSITORY_URL | https://github.com/welfare-state-analytics/riksdagen-corpus.git |
| RIKSPROT_REPOSITORY_TAG | Target corpus version. Must be a valid Github tag               |
| SPARV_DATADIR           | Sparv data folder                                               |
| STANZA_DATADIR          | Stanza data folder                                              |

```bash
RIKSPROT_DATA_FOLDER="/path/to/data/folder"
RIKSPROT_REPOSITORY_URL="https://github.com/welfare-state-analytics/riksdagen-corpus.git"
RIKSPROT_REPOSITORY_TAG="vx.y.z"
SPARV_DATADIR="/path/to/sparv_datadir"
STANZA_DATADIR="/path/to/stanza_datadir"
```

# Appendix


## Setup a local copy of riksdagen-corpus Github repository

If **riksdagen-corpus** repository folder already exists, then do an update:

```bash
cd /path/to/git/repository
git pull
```

If repository folder doesn't exist:

```bash
cd /path/to/parent-folder
git clone git@github.com:welfare-state-analytics/pyriksprot_tagger.git
```

You need to checkout the specific tag that you want to process:

```bash
cd /path/to/git/repository
git checkout vx.y.z
```

Make sure to update file timestamps to latest commit timestamp!

```bash
cd /path/to/pyriksprot-tagger
./pyriksprot_tagger/scripts/update-timestamps
```


## Install pyriksprot-tagger from PyPI

Verify current Python version (`pyenv` is recommended for easy switch between versions).

 Create a new Python virtual environment (sandbox):

```bash
cd /some/folder
mkdir riksprot_tagging
cd riksprot_tagging
python -m venv .venv
source .venv/bin/activate
```

Install the pipeline and run setup script.

```bash
pip install pyriksprot_tagger
setup-pipeline
```

To tag protocols you first need to activate the installed environment, and then follow steps above on how to tag protocols using snakemake.


```bash
cd /some/folder/pyriksprot
source .venv/bin/activate
```

## Create or update the repository using snakemake (not recommended)

This is an alternative way of updating the corpus repository.

```bash
% cd /path/to/pyriksprot-tagger/folder
```

If you want to create a new clone of the repository:

```bash
% make full-clone-repository
```

If you want to update an existing repository:
```bash
% make full-pull-repository
```

If you want to save space and do a shallow clone
```bash
% make shallow-update-repository
```

Update timestamp of repository work folder files to match last commit timestamp. Important! This is **required** if you use Snakemake when tagging:

```bash
% make update-repository-timestamps
```

## How to annotate protocols using snakemake (not recommended)

 Annotate using default settings:

```bash
make annotate
```

Annotate a single year (and set cpu count).

```bash
make annotate YEAR=1960 CPU_COUNT=1
```

Call snakemake directly:

```bash
nohup make annotate PROCESSES_COUNT=4 >& run.log &
```
or
```bash
nohup poetry run snakemake --config -j4 --keep-going --keep-target-files &
```
