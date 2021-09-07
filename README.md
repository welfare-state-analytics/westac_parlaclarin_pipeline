# Parla-Clarin Workflow

This package implements Stanza part-of-speech annotation of ParlaClarin XML files.

## Prerequisites

- Git
- Python 3.8.5^
- GNU make
- Poetry

## Install

Clone this repository:

1. cd a-project-directory-of-your-choosing
1. git clone git@github.com:welfare-state-analytics/westac_parlaclarin_pipeline
1. cd westac_parlaclarin_pipeline

Or install python package:

1. poetry init --python 3.8.5
1. poetry install westac_parlaclarin_pipeline
1. poetry install westac_parlaclarin_pipeline

## Run annotation

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
