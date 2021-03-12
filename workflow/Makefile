# This file implements a Github Parla-Clarin to tagged text pipeline
################################################################################
#                               CONFIGURATION                                  #
################################################################################

# snakemake options: https://snakemake.readthedocs.io/en/stable/executing/cli.html#all-options

.DEFAULT_GOAL=lint

SHELL 							:= /bin/bash

ROOT_FOLDER 					:= /data/riksdagen_corpus_data

REPOSITORY_NAME 				:= riksdagen-corpus
SOURCE_PARLA_CLARIN_DATA_FOLDER := $(ROOT_FOLDER)/$(REPOSITORY_NAME)/data/new-parlaclarin
TARGET_EXPORT_FOLDER 			:= $(ROOT_FOLDER)/$(REPOSITORY_NAME)-exports

SOURCE_REPOSITORY_URL 			:= https://github.com/welfare-state-analytics/$(REPOSITORY_NAME).git

PARLA_CLARIN_TEXT_FOLDER = $(TARGET_EXPORT_FOLDER)/speech_xml
PARLA_CLARIN_XML_FILES = $(wildcard $(SOURCE_PARLA_CLARIN_DATA_FOLDER)/*.xml)
PARLA_CLARIN_TEXT_ZIP = $(PARLA_CLARIN_TEXT_FOLDER)/$(REPOSITORY_NAME).txt.zip

.DELETE_ON_ERROR:
.SECONDARY:

# optional_executables = dot
# k = $(foreach exec,$(optional_executables),\
# 	$(if $(shell which $(exec)),some string,$(warning consider installing "$(exec)")))

# mandatory_executables = snakemake sparv
# $(foreach exec,$(mandatory_executables),
# 	$(if $(shell which $(exec)),some string,$(error "$(exec)" not in path, please install)))

################################################################################
#                                RECIPIES                                      #
################################################################################

$(TARGET_EXPORT_FOLDER):
	@mkdir -p $(TARGET_EXPORT_FOLDER)

$(PARLA_CLARIN_TEXT_FOLDER):
	@mkdir -p $(TARGET_EXPORT_FOLDER)/parla_clarin_text

clean:
	@rm -rf $(PARLA_CLARIN_TEXT_FOLDER)

.ONESHELL:
init_repository: $(TARGET_EXPORT_FOLDER) $(PARLA_CLARIN_TEXT_FOLDER) $(ROOT_FOLDER)/$(REPOSITORY_NAME)
	@echo "init"
	@if [ ! -d "$(ROOT_FOLDER)" ]; then
		echo "error: data folder $(ROOT_FOLDER) not found."
		exit 64
	fi
	@if [ -d "$(ROOT_FOLDER)/$(REPOSITORY_NAME)" ]; then
		echo "info: repository folder exists and overwrite is prohibited."
		exit 0
	fi
	@echo "info: creating shallow copy of $(SOURCE_REPOSITORY_URL)"
	@cd $(ROOT_FOLDER)
	@git clone --depth 1 $(SOURCE_REPOSITORY_URL)
	@echo "info: done!"
	@cd - > /dev/null 2>&1

.ONESHELL:
update_repository:
	poetry run snakemake -j1 update_repository

# See https://snakemake.readthedocs.io/en/stable/project_info/faq.html#git-is-messing-up-the-modification-times-of-my-input-files-what-can-i-do
.ONESHELL:
update_repository_timestamps:
	@gitmtim(){ \
		local f \
		for f; do \
			touch -d @0`git log --pretty=%at -n1 -- "$f"` "$f" \
		done \
	} \
	gitmodtimes(){ \
		for f in $(git ls-tree -r $(git rev-parse --abbrev-ref HEAD) --name-only); do \
			gitmtim $f \
		done \
	} \
	gitmodtimes

.PHONY: help clean init_repository update_repository

parla_clarin_to_text:
	@snakemake -p -j1

dag:
	@snakemake --dag | dot | display

dag_pdf:
	@snakemake --dag | dot -Tpdf > dag.pdf

help:
	@echo "Lower level recepies: "
	@echo " make clean               Clean target Snakemake folder"
	@echo " make init_repository     Create shallow clone of Para-Clarin repository"
	@echo " make update_repository   Shallow update of  Para-Clarin repository"
	@echo " make help                Display this message"
	@echo "  "
