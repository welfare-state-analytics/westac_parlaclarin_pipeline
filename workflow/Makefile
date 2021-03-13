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
	@poetry run snakemake -j1 init_repository

.ONESHELL:
update_repository:
	@poetry run snakemake -j1 update_repository

.ONESHELL:
update_repository_timestamps:
	@poetry run snakemake -j1 update_repository_timestamps

.PHONY: help clean init_repository update_repository

parla_clarin_to_text:
	@snakemake -p -j1

dag:
	@snakemake --dag | dot | display

dag_pdf:
	@snakemake --dag | dot -Tpdf > dag.pdf

help:
	@echo "Lower level recepies: "
	@echo " make clean               			Clean target Snakemake folder"
	@echo " make init_repository     			Create shallow clone of Para-Clarin repository"
	@echo " make update_repository   			Shallow update of  Para-Clarin repository"
	@echo " make update_repository_timestamps   Shallow update of  Para-Clarin repository"
	@echo " make help                			Display this message"
	@echo "  "
