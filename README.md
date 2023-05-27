# Riksdagens Protokoll Part-Of-Speech Tagging

This package implements part-of-speech tagging of `Riksdagens Protokoll` Parla-CLARIN XML files.

## Overview

Prerequisites:
 - [ ] Programs `git`, `pyenv` and `poetry` installed (recommended).
 - [ ] Latest version of **welfare-state-analytics/pyriksprot_tagger** installed
 - [ ] Latest version of ParlaCLARIN Github repository
 - [ ] Updated configuration (see below)
 - [ ] Data models for Sparv and Stanza

If you want to use snakemake:
 - [ ] Edit options (target name) in workflow/config/config.yml
 - [ ] Run **make annotate**

If you want to use the **tag** script (preferred, faster):

 - [ ] Run **PYTHONPATH=. nohup ./tag.sh --target-folder /path/to/output/data > tag-it.version.log &**

## Install `pyriksprot` tagger

### Clone tagger repository (recommended)

Prerequisites:
 - [ ] Version control system `git` installed.
 - [ ] Python version manager `pyenv` (recommended).
 - [ ] Python package manager `poetry` (recommended).

```bash
% cd /path/to/any/folder
% git clone git@github.com:welfare-state-analytics/pyriksprot_tagger
% cd pyriksprot_tagger
% pyenv local 3.11.3
% poetry shell
% pip install torch
% poetry install
```

### Install tagger in an isolated Python virtual environment

Prerequisites:
 - [ ] Python version manager `pyenv`
 - [ ] Gnu `make`

Install the `pyriksprot` packages:

```bash
% mkdir /path/to/new/folder
% cd /path/to/new/folder
% pyenv local 3.11.3
% python -m venv .venv
% . ./.venv/bin/activate
% pip install torch pyriksprot pyriksprot_tagger
% wget https://raw.githubusercontent.com/welfare-state-analytics/pyriksprot_tagger/main/Makefile
% wget https://raw.githubusercontent.com/welfare-state-analytics/pyriksprot_tagger/main/Makefile.dev

```

## Update configuration

Prerequisites:
 - [ ] Språkbanken Sparvs data models (http://github.com/spraakbanken).
 - [ ] Stanza models (also part of Sparvs models).

Update or create config file .env in `pyriksprot_tagger` folder with the following environment variables:

| Environment variable | Description |
| --- | --- |
| RIKSPROT_DATA_FOLDER | Parent folder (location) of Riksdagens corpus data folder |
| RIKSPROT_REPOSITORY_URL |  https://github.com/welfare-state-analytics/riksdagen-corpus.git |
| RIKSPROT_REPOSITORY_TAG | Target corpus version. Must be a valid Github tag |
| SPARV_DATADIR | Sparv data folder |
| STANZA_DATADIR | Stanza data folder |

```bash
RIKSPROT_DATA_FOLDER="/path/to/data/folder"
RIKSPROT_REPOSITORY_URL="https://github.com/welfare-state-analytics/riksdagen-corpus.git"
RIKSPROT_REPOSITORY_TAG="vx.y.z"
SPARV_DATADIR="/path/to/sparv_datadir"
STANZA_DATADIR="/path/to/stanza_datadir"
```

## Setup ParlaCLARIN data repository

Prerequisites:
 - [ ] Version control system `git` installed.

If **pyriksprot_tagger** repository folder already exists, then do an update:

```bash
% cd /path/to/git/repository
% git pull
% git checkout vx.y.z
```

If repository folder doesn't exist:

```bash
% cd "some-folder"
% git clone git@github.com:welfare-state-analytics/pyriksprot_tagger.git
% git checkout vx.y.z
```

### Create or update Riksdagens Corpus data using make

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

Update timestamp of repository work folder files to match last commit timestamp. This is required if you use Snakemake when tagging (important!):

```bash
% make update-repository-timestamps
```

## Create metadata database:

 - [ ] Pull or clone latest version of **welfare-state-analytics/pyriksprot**
 - [ ] Update configuration (specify tag) to use in **pyriksprot/.env**
 - [ ] Run **make metadata**

## Create speech corpus

 - [ ] Pull or clone latest version of **welfare-state-analytics/pyriksprot**
 - [ ] Update configuration (specify tag) to use in **pyriksprot/.env**
 - [ ] Run make extract-speeches-to-feather


## How to annotate protocols using snakemake (not recommended)


 - Annotate using default settings.
```bash
make annotate
```

 - Update a single year (and set cpu count).

```bash
make annotate YEAR=1960 CPU_COUNT=1
```

 - Call snakemake directly:

```bash
$ nohup make annotate PROCESSES_COUNT=4 >& run.log &
or
$ nohup poetry run snakemake -j4 --keep-going --keep-target-files &
```

```bash
nohup poetry run snakemake --config -j4 --keep-going --keep-target-files &
```

## Install from PyPI (not recommended)

Verify current Python version (`pyenv` is recommended for easy switch between versions).

 - Create a new Python virtual environment (sandbox):

```bash
cd /some/folder
mkdir riksprot_tagging
cd riksprot_tagging
python -m venv .venv
source .venv/bin/activate
```

 - Install the pipeline and run setup script.

```bash
pip install pyriksprot_tagger
setup-pipeline
```

To tag protocols you first need to activate the installed environment, and then follow steps above on how to tag protocols using snakemake.


```bash
cd /some/folder/pyriksprot
source .venv/bin/activate
```
