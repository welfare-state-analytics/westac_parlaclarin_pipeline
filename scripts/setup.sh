#!/bin/bash

# script_folder=`dirname "${BASH_SOURCE[0]}"`

settings=`poetry run python ./scripts/config_value.py  --config-name=config.yml \
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
speech_xml_folder=${settings[4]}
word_frequency_filename=${settings[5]}

if [ -d "$root_folder" ]; then
    echo "error: $root_folder is missing"
    exit 64
fi

if [ ! -d "$repository_folder" ]; then
    echo "info: initializing repository at $repository_folder"
    make init-repository
    make update-repository-timestamps
fi

if [ ! -d "$speech_xml_folder" ]; then
    echo "info: creating speech xml folder $speech_xml_folder"
    mkdir -p "$speech_xml_folder"
fi

if [ ! -d "$root_folder/sparv" ]; then
    echo "error: sparv folder $root_folder/sparv does not exist!"
    exit 64
fi

if [ ! -d "$root_folder/sparv/models" ]; then
    echo "error: sparv models folder $root_folder/sparv/models does not exist!"
    exit 64
fi

if [ ! -f "${speech_xml_folder}/config.yaml" ]; then
    cp ./resources/sparv/speech_xml_config.yaml "$speech_xml_folder/config.yaml"
fi

if [ ! -L ./work_dir ]; then
    ln -s $root_folder work_dir
fi

echo "to sparv it:"
echo " cd ${speech_xml_folder}"
echo " sparv run -j6"
