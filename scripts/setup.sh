#!/bin/bash


settings=`poetry run python scripts/config_value.py  --config-name=config.yml \
    config.work_folders.data_folder \
    config.parla_clarin.repository_folder \
    config.parla_clarin.repository_url \
    config.parla_clarin.folder \
    config.extract_speeches.folder \
    config.word_frequency.filename \
    `

root_folder=${settings[0]}
repository_folder=${settings[1]}
repository_url=${settings[2]}
source_folder=${settings[3]}
target_folder=${settings[4]}
word_frequency_filename=${settings[5]}

if [ -d "$root_folder" ]; then
    echo "error: $root_folder "
    exit 64
fi

if [ ! -d "$repository_folder" ]; then
    echo "info: initializing repository at $repository_folder"
    make init-repository
    make update-repository-timestamps
fi

if [ ! -d "$target_folder" ]; then
    echo "info: creating target folder $target_folder"
    mkdir -p "$target_folder"
fi

if [ ! -d "$root_folder/sparv" ]; then
    echo "error: sparv folder $root_folder/sparv does not exist!"
    exit 64
fi

if [ ! -d "$root_folder/sparv/models" ]; then
    echo "error: sparv models folder $root_folder/sparv/models does not exist!"
    exit 64
fi
