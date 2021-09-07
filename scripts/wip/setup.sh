#!/bin/bash
# Sets up working folders for ParlaClarin pipeline.
#
# script_folder=`dirname "${BASH_SOURCE[0]}"`

settings=$( poetry run python ./scripts/config_value.py  --config-name=config.yml \
    config.work_folders.data_folder \
    config.parla_clarin.repository_folder \
    config.parla_clarin.repository_url \
    config.parla_clarin.repository_branch \
    config.parla_clarin.folder \
    config.extract_speeches.folder \
    config.annotated_folder \
    config.word_frequency.filename  )

set -f
array=($(echo "$settings" | tr ' ' '\n'))
root_folder="${array[0]}"
repository_folder=${array[1]}
repository_url=${array[2]}
repository_branch=${array[3]}
source_folder=${array[4]}
speech_xml_folder=${array[5]}
annotated_folder=${array[6]}
word_frequency_filename=${array[7]}

echo "Using settings: "
echo "  root_folder=${root_folder}"
echo "  repository_folder=${repository_folder}"
echo "  repository_url=${repository_url}"
echo "  repository_branch=${repository_branch}"
echo "  source_folder=${source_folder}"
echo "  speech_xml_folder=${speech_xml_folder}"
echo "  annotated_folder=${annotated_folder}"
echo "  word_frequency_filename=${word_frequency_filename}"

exit 0

if [ -d "$root_folder" ]; then
    echo "error: $root_folder is missing"
    exit 64
fi

if [ ! -d "$repository_folder" ]; then
    echo "info: initializing repository at $repository_folder"
    make init-repository
    make update-repository-timestamps
fi

# if [ ! -d "$speech_xml_folder" ]; then
#     echo "info: creating speech xml folder $speech_xml_folder"
#     mkdir -p "$speech_xml_folder"
# fi

if [ ! -d "$annotated_folder" ]; then
    echo "info: creating annotation target folder $annotated_folder"
    mkdir -p "$annotated_folder"
fi

if [ ! -d "$root_folder/sparv" ]; then
    echo "error: sparv folder $root_folder/sparv does not exist!"
    exit 64
fi

if [ ! -d "$root_folder/sparv/models" ]; then
    echo "error: sparv models folder $root_folder/sparv/models does not exist!"
    exit 64
fi

# if [ ! -f "${speech_xml_folder}/config.yaml" ]; then
#     cp ./resources/sparv/speech_xml_config.yaml "$speech_xml_folder/config.yaml"
# fi

if [ ! -L ./work_dir ]; then
    ln -s $root_folder work_dir
fi

# echo "to sparv it:"
# echo " cd ${speech_xml_folder}"
# echo " sparv run -j6"
