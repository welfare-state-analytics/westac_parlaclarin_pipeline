#!/bin/bash

echo "script is deprecated/outdated"
exit 64

# script_folder=`dirname "${BASH_SOURCE[0]}"`

settings=`poetry run python ./scripts/config_value.py  configs/config.yml \
    config.data_folder \
    config.source.repository_folder \
    config.source.repository_url \
    config.source.repository_tag \
    config.source.folder \
    config.target.folder \
    config.dehyphen.tf_filename \
    `

root_folder=${settings[0]}
repository_folder=${settings[1]}
repository_url=${settings[2]}
repository_tag=${settings[3]}
source_folder=${settings[4]}
target_folder=${settings[5]}
word_frequency_filename=${settings[6]}

.ONESHELL:
$(root_folder):
	@ if [ -d "$$root_folder" ]; then  \
		echo "error: $$root_folder is missing" ; \
		exit 64 ; \
	fi

.ONESHELL:
$(repository_folder):
	if [ ! -d "$(repository_folder)" ]; then \
		echo "info: initializing repository at $(repository_folder)" ; \
		make init-repository ; \
		make update-repository-timestamps ; \
	fi

.ONESHELL:
$(target_folder):
	if [ ! -d "$(target_folder)" ]; then \
		echo "info: annotating folder $(target_folder)" ; \
		mkdir -p "$(target_folder)" ; \
	fi

.ONESHELL:
$(root_folder)/sparv
if [ ! -d "$(root_folder)/sparv" ]; then \
    echo "error: sparv folder $(root_folder)/sparv does not exist!" ; \
    exit 64 ; \
fi

.ONESHELL:
$(root_folder)/sparv/models:
	if [ ! -d "$(root_folder)/sparv/models" ]; then \
		echo "error: sparv models folder $(root_folder)/sparv/models does not exist!" ; \
		exit 64 ; \
	fi

.ONESHELL:
$(root_folder)/work_dir:
	if [ ! -L ./work_dir ]; then \
		ln -s $(root_folder) $(HOME)/work_dir
	fi

# .ONESHELL:
# if [ ! -d ./work_dir/sparv_workdir ]; then
#     mkdir ./work_dir/sparv_workdir
#     cp ./resources/sparv/speech_xml_config.yaml ./work_dir/sparv_workdir
#     ln -s $target_folder ./work_dir/sparv_workdir/source
# fi

# cd ./work_dir/sparv_workdir
# poetry shell
# sparv run -j6
