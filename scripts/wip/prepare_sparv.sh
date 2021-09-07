#!/bin/bash


settings=`poetry run python ./scripts/config_value.py  --config-name=config.yml \
    config.work_folders.data_folder \
    config.parla_clarin.repository_folder \
    config.parla_clarin.repository_url \
    config.parla_clarin.repository_branch \
    config.parla_clarin.folder \
    config.extract_speeches.folder \
    config.annotated_folder \
    config.word_frequency.filename \
    `

root_folder=${settings[0]}
repository_folder=${settings[1]}
repository_url=${settings[2]}
repository_branch=${settings[3]}
source_folder=${settings[4]}
speech_xml_folder=${settings[5]}
annotated_folder=${settings[6]}
word_frequency_filename=${settings[7]}

# Move empty files: Sparv doesn't like that

empty_folder=${speech_xml_folder}/empty_protocols

find ${speech_xml_folder} -type f ! -exec grep -q 'speech' {} \; -print > ${empty_folder}/filenames.txt
#find ${speech_xml_folder} -type f ! -exec grep -q 'speech' {} \; -print0 | xargs -0 -I {} mv {} ${empty_folder}

find ./speech_xml/ -type f ! -exec grep -q 'speech' {} \; -print0 | xargs -0 -I {} mv {} ./empty_protocols

