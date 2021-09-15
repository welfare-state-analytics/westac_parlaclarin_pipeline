#################################################################################################################
# Utility recepies for runninh the ParlaClarin pipeline
#################################################################################################################

.DEFAULT_GOAL=help
SHELL:=/bin/bash

.DELETE_ON_ERROR:
.SECONDARY:

PYPROJECT := $(shell test -f pyproject.toml && echo -n "yes")
ifeq ($(strip $(PYPROJECT)), yes)
	POETRY=poetry run
else
	POETRY=
endif

OPTS =

# CUSTOM_CONFIG := $(shell test -f config.yml && echo -n "yes")
# ifeq ($(strip $(PYPROJECT)), yes)
# 	OPTS := --configfile ./config.yml --config CUSTOM_CONFIG=true
# endif

ifdef YEAR
OPTS := $(OPTS) year_filter=$(YEAR)
endif

ifdef DISABLE_GPU
OPTS := $(OPTS) disable_gpu=1
endif

ifdef PROCESSES_COUNT
OPTS := $(OPTS) processes=$(PROCESSES_COUNT)
endif

ifneq ($(OPTS),)
OPTS := --config $(OPTS)
endif

# ifdef BATCH_DIVISOR
# OPTS := $(OPTS) --batch tag_protocols=1/$(BATCH_DIVISOR)
# endif


CPU_COUNT = 4

# optional_executables = dot
# k = $(foreach exec,$(optional_executables),\
# 	$(if $(shell which $(exec)),some string,$(warning consider installing "$(exec)")))

mandatory_executables=snakemake sparv

#$(foreach exec,$(mandatory_executables), $(if $(shell which $(exec)),some string,$(error "$(exec)" not in path, please install)))

CORPUS_REPOSITORY := /data/riksdagen_corpus_data/riksdagen-corpus/

clean:
	@$(POETRY) snakemake -j1 --cleanup-shadow

unlock:
	@$(POETRY) snakemake -j1 --unlock

init-repository:
	@$(POETRY) snakemake -j1 init_repository

update-repository:
	@$(POETRY) snakemake -j1 update_repository

.PHONY: tf
tf:
	@$(POETRY) snakemake -j4 word_frequency $(OPTS)

# Alternative: https://github.com/MestreLion/git-tools/

.ONESHELL:
update-repository-timestamps:
	@curl -s https://raw.githubusercontent.com/MestreLion/git-tools/main/git-restore-mtime -o /tmp/git-restore-mtime \
		&& pushd . \
		&& cd $(CORPUS_REPOSITORY) \
		&& pwd \
		&& python /tmp/git-restore-mtime --commit-time \
		&& popd

update-repository-timestamps-snakemake:
	# @if [[ "$$OS" == "Windows_NT" ]]; then
	# 	echo "note: Windows OS detected. Please run from Git BASH CLI instead"
	# 	echo "usage: scripts/git_update_mtime.sh $(CORPUS_REPOSITORY)"
	# 	exit 0
	# fi
	@$(POETRY) snakemake -j1 update_repository_timestamps

annotate: unlock
	@$(POETRY) snakemake -j$(CPU_COUNT) --keep-going --keep-target-files $(OPTS)

extract-speeches-workflows:
	@echo "This recipe is deprecated"
	@echo "$(POETRY) snakemake -p -j4"

workflow-dag:
	@$(POETRY) snakemake --dag | dot | display

workflow-dag-pdf:
	@$(POETRY) snakemake --dag | dot -Tpdf > dag.pdf

clean-workflow:
	@$(POETRY) snakemake -j1 --delete-all-output

lint-workflow:
	@$(POETRY) snakemake -j1 lint

test-workflow:
	@$(POETRY) snakemake -j1 --config config_filename=test_config.yml

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
