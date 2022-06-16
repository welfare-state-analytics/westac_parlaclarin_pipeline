#!/bin/bash


settings=`poetry run python ./scripts/config_value.py  --config-name=config.yml \
    config.data_folder \
    config.corpus.repository_folder \
    config.corpus.repository_url \
    config.corpus.repository_tag \
    config.corpus.source_folder \
    config.extract_opts.folder \
    config.tagged_frames_folder \
    config.tf_opts.filename \
    `

root_folder=${settings[0]}
repository_folder=${settings[1]}
repository_url=${settings[2]}
repository_tag=${settings[3]}
source_folder=${settings[4]}
speech_xml_folder=${settings[5]}
tagged_frames_folder=${settings[6]}
word_frequency_filename=${settings[7]}

# Move empty files: Sparv doesn't like that

empty_folder=${speech_xml_folder}/empty_protocols

find ${speech_xml_folder} -type f ! -exec grep -q 'speech' {} \; -print > ${empty_folder}/filenames.txt
#find ${speech_xml_folder} -type f ! -exec grep -q 'speech' {} \; -print0 | xargs -0 -I {} mv {} ${empty_folder}

find ./speech_xml/ -type f ! -exec grep -q 'speech' {} \; -print0 | xargs -0 -I {} mv {} ./empty_protocols

