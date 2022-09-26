#!/bin/bash
# Sets up working folders for ParlaClarin pipeline.
#
# script_folder=`dirname "${BASH_SOURCE[0]}"`

settings=$( poetry run python ./scripts/config_value.py  configs/default.yml \
    config.data_folder \
    config.corpus.repository_folder \
    config.corpus.repository_url \
    config.corpus.repository_tag \
    config.corpus.source_folder \
    config.extract_opts.folder \
    config.tagged_frames_folder \
    config.tf_opts.filename  )

set -f
array=($(echo "$settings" | tr ' ' '\n'))
root_folder="${array[0]}"
repository_folder=${array[1]}
repository_url=${array[2]}
repository_tag=${array[3]}
source_folder=${array[4]}
speech_xml_folder=${array[5]}
tagged_frames_folder=${array[6]}
word_frequency_filename=${array[7]}

echo "Using settings: "
echo "  root_folder=${root_folder}"
echo "  repository_folder=${repository_folder}"
echo "  repository_url=${repository_url}"
echo "  repository_tag=${repository_tag}"
echo "  source_folder=${source_folder}"
echo "  speech_xml_folder=${speech_xml_folder}"
echo "  tagged_frames_folder=${tagged_frames_folder}"
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

if [ ! -d "$tagged_frames_folder" ]; then
    echo "info: creating annotation target folder $tagged_frames_folder"
    mkdir -p "$tagged_frames_folder"
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
