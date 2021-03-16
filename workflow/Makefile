.DEFAULT_GOAL=help
SHELL:=/bin/bash

.DELETE_ON_ERROR:
.SECONDARY:

# optional_executables = dot
# k = $(foreach exec,$(optional_executables),\
# 	$(if $(shell which $(exec)),some string,$(warning consider installing "$(exec)")))

# mandatory_executables = snakemake sparv
# $(foreach exec,$(mandatory_executables),
# 	$(if $(shell which $(exec)),some string,$(error "$(exec)" not in path, please install)))

init_repository:
	@poetry run snakemake -j1 init_repository

update_repository:
	@poetry run snakemake -j1 update_repository

update_repository_timestamps:
	@poetry run snakemake -j1 update_repository_timestamps

extract_speeches:
	@poetry run snakemake -p -j4

dag:
	@poetry run snakemake --dag | dot | display

dag_pdf:
	@poetry run snakemake --dag | dot -Tpdf > dag.pdf

clean:
	@poetry run snakemake -j1 --delete-all-output

lint:
	@poetry run snakemake -j1 lint

run_test:
	@poetry run snakemake -j1 --config config_filename=test_config.yml

.PHONY: help clean init_repository update_repository update_repository_timestamps extract_speeches dag dag_pdf

help:
	@echo "Lower level recepies: "
	@echo " make clean               			Clean target Snakemake folder"
	@echo " make init_repository     			Create shallow clone of Para-Clarin repository"
	@echo " make update_repository   			Shallow update of  Para-Clarin repository"
	@echo " make update_repository_timestamps   Shallow update of  Para-Clarin repository"
	@echo " make extract_speeches				Extract speeches from ParaClarin XML corpus"
	@echo " make run_test                		Runs against test repository"
	@echo " make help                			Display this message"
	@echo " make lint                			Run Snakemake's linter"
	@echo "  "
