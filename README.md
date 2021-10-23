# Riksdagens Protokoll Part-Of-Speech Tagging (Parla-Clarin Workflow)

This package implements Stanza part-of-speech annotation of `Riksdagens Protokoll` Parla-Clarin XML files.

## Prerequisites

- A bash-enabled environment (Linux or Git Bash on windows)
- Git
- Python 3.8.5^
- GNU make (install i)

## Install

(This workflow will be simplified)

Verify current Python version (`pyenv` is recommended for easy switch between versions).

Create a new Python virtual environment (sandbox):

```bash
cd /some/folder
mkdir westac_parlaclarin_pipeline
cd westac_parlaclarin_pipeline
python -m venv .venv
source .venv/bin/activate
```

Install the pipeline and run setup script.

```bash
pip install westac_parlaclarin_pipeline
setup-pipeline
```

## Initialize local clone of Parla-CLARIN repository

## Run PoS tagging

Move to sandbox and activate virtual environment:

```bash
cd /some/folder/westac_parlaclarin_pipeline
source .venv/bin/activate
```

Update repository:

```bash
make update-repository
make update-repository-timestamps
```

Update all (changed) annotations:

```bash
make annotate
```

Update a single year (and set cpu count):

```bash
make annotate YEAR=1960 CPU_COUNT=1
```

## Configuration


```yaml
work_folders: !work_folders &work_folders
  data_folder: /data/riksdagen_corpus_data

parla_clarin: !parla_clarin &parla_clarin
  repository_folder: /data/riksdagen_corpus_data/riksdagen-corpus
  repository_url: https://github.com/welfare-state-analytics/riksdagen-corpus.git
  repository_branch: dev
  folder: /data/riksdagen_corpus_data/riksdagen-corpus/corpus

extract_speeches: !extract_speeches &extract_speeches
  folder: /data/riksdagen_corpus_data/riksdagen-corpus-exports/speech_xml
  template: speeches.cdata.xml
  extension: xml

word_frequency: !word_frequency &word_frequency
  <<: *work_folders
  filename: riksdagen-corpus-term-frequencies.pkl

dehyphen: !dehyphen &dehyphen
  <<: *work_folders
  whitelist_filename: dehyphen_whitelist.txt.gz
  whitelist_log_filename: dehyphen_whitelist_log.pkl
  unresolved_filename: dehyphen_unresolved.txt.gz

config: !config
    work_folders: *work_folders
    parla_clarin: *parla_clarin
    extract_speeches: *extract_speeches
    word_frequency: *word_frequency
    dehyphen: *dehyphen
    annotated_folder: /data/riksdagen_corpus_data/annotated
```
