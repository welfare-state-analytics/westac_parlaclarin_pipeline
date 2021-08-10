#################################################################################################################
# Utility recepies for runninh the ParlaClarin pipeline
#################################################################################################################

.DEFAULT_GOAL=help
SHELL:=/bin/bash

.DELETE_ON_ERROR:
.SECONDARY:

# optional_executables = dot
# k = $(foreach exec,$(optional_executables),\
# 	$(if $(shell which $(exec)),some string,$(warning consider installing "$(exec)")))

mandatory_executables=snakemake sparv

#$(foreach exec,$(mandatory_executables), $(if $(shell which $(exec)),some string,$(error "$(exec)" not in path, please install)))

init-repository:
	@poetry run snakemake -j1 init_repository

update-repository:
	@poetry run snakemake -j1 update_repository

update-repository-timestamps:
	@poetry run snakemake -j1 update_repository_timestamps

extract-speeches-workflows:
	@poetry run snakemake -p -j4

workflow-dag:
	@poetry run snakemake --dag | dot | display

workflow-dag-pdf:
	@poetry run snakemake --dag | dot -Tpdf > dag.pdf

clean-workflow:
	@poetry run snakemake -j1 --delete-all-output

lint-workflow:
	@poetry run snakemake -j1 lint

test-workflow:
	@poetry run snakemake -j1 --config config_filename=test_config.yml

.PHONY: help-workflow clean-workflow
.PHONY: init-repository update-repository update-repository-timestamps
.PHONY: extract-speeches-workflow
.PHONY: dag-workflow dag-pdf-workflow

help-workflow:
	@echo "Higher level recepies: "
	@echo " make clean-workflow					Clean target Snakemake folder"
	@echo " make init-repository				Create shallow clone of Para-Clarin repository"
	@echo " make update_repository				Shallow update of Para-Clarin repository"
	@echo " make update-repository-timestamps   Update file modify dates of files checked out from repository"
	@echo " make extract-speeches-workflow		Extract speeches from ParaClarin XML corpus"
	@echo " make test-workflow					Runs against test repository"
	@echo " make help-workflow  				Display this message"
	@echo " make lint-workflow					Run Snakemake's linter"
	@echo "  "
