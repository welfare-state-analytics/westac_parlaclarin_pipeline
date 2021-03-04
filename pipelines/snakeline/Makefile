# This file implements a Github Parla-Clarin to tagged text pipeline
################################################################################
#                               CONFIGURATION                                  #
################################################################################

.DEFAULT_GOAL=lint

SHELL 							:= /bin/bash

ROOT_FOLDER 					:= /data/riksdagen_corpus_data

REPOSITORY_NAME 				:= riksdagen-corpus
SOURCE_PARLA_CLARIN_DATA_FOLDER := $(ROOT_FOLDER)/$(REPOSITORY_NAME)/data/new-parlaclarin
TARGET_EXPORT_FOLDER 			:= $(ROOT_FOLDER)/$(REPOSITORY_NAME)-exports

SOURCE_REPOSITORY_URL 			:= https://github.com/welfare-state-analytics/$(REPOSITORY_NAME).git

PARLA_CLARIN_TEXT_FOLDER = $(TARGET_EXPORT_FOLDER)/parla_clarin_text
PARLA_CLARIN_XML_FILES = $(wildcard $(SOURCE_PARLA_CLARIN_DATA_FOLDER)/*.xml)
PARLA_CLARIN_TEXT_ZIP = $(PARLA_CLARIN_TEXT_FOLDER)/$(REPOSITORY_NAME).txt.zip

.DELETE_ON_ERROR:
.SECONDARY:

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
init_repository $(TARGET_EXPORT_FOLDER) $(PARLA_CLARIN_TEXT_FOLDER) $(ROOT_FOLDER)/$(REPOSITORY_NAME)
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
	@echo "Updating Para-Clarin XML repository"
	@if [ ! -d "$(ROOT_FOLDER)/$(REPOSITORY_NAME)" ]; then
		echo "error: target folder $(LOCAL_REPOSITORY) not found!"
		exit 64
	fi
	@cd $(ROOT_FOLDER)/$(REPOSITORY_NAME)
	@git fetch --depth 1 && git reset --hard origin && git clean -dfx
	@for filename in $(PARLA_CLARIN_TEXT_FOLDER)/*.txt ; do
		if [ ! -f "$(SOURCE_PARLA_CLARIN_DATA_FOLDER)/$$(basename $${filename%.txt}).xml" ] ; then
			rm -f $$filename ;
			zip -qdo $(PARLA_CLARIN_TEXT_ZIP) $$(notdir $${filename})
		fi
	done
	@cd - > /dev/null 2>&1

.PHONY: help clean init_repository update_repository

parla_clarin_to_text:
	@snakemake -p -j1


help:
	@echo "Lower level recepies: "
	@echo " make clean               Clean target Snakemake folder"
	@echo " make init_repository     Create shallow clone of Para-Clarin repository"
	@echo " make update_repository   Shallow update of  Para-Clarin repository"
	@echo " make help                Display this message"
	@echo "  "
