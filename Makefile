.DEFAULT_GOAL=lint

include ./workflow/Makefile

ifndef RIKSPROT_DATA_FOLDER
$(error RIKSPROT_DATA_FOLDER is undefined)
endif

SHELL := /bin/bash
SOURCE_FOLDERS=workflow tests
PACKAGE_FOLDER=workflow scripts resources
#PYTEST_ARGS=--durations=0 --cov=$(PACKAGE_FOLDER) --cov-report=xml --cov-report=html tests
PYTEST_ARGS=--no-cov tests
RUN_TIMESTAMP := $(shell /bin/date "+%Y-%m-%d-%H%M%S")

faster-release: bump.patch tag publish

fast-release: clean-dev tidy build guard-clean-working-repository bump.patch tag publish

release: ready guard-clean-working-repository bump.patch tag publish

ready: production-mode tools clean-dev tidy test lint requirements.txt build

build: requirements.txt-to-git
	@poetry build

publish:
	@poetry publish

lint: tidy pylint

tidy: black isort

tidy-to-git: guard-clean-working-repository tidy
	@status="$$(git status --porcelain)"
	@if [[ "$$status" != "" ]]; then
		@git add .
		@git commit -m "📌 make tidy"
		@git push
	fi

.PHONY: production-mode edit-mode

.ONESHELL: production-mode
production-mode:
	@if grep -e "pyriksprot = .*develop" pyproject.toml > /dev/null ; then \
		poetry remove pyriksprot ; \
		pip uninstall pyriksprot ; \
		poetry add pyriksprot ; \
	fi

.ONESHELL: edit-mode
edit-mode:
	@if ! grep -e "pyriksprot = .*develop" pyproject.toml > /dev/null ; then \
		echo "installing pyriksprot in edit mode" ; \
		cp -f pyproject.toml pyproject.tmp ; \
		sed -i '/pyriksprot = /c\pyriksprot = {path = "../pyriksprot", develop = true}' pyproject.tmp ; \
		poetry remove pyriksprot >& /dev/null ; \
		poetry run pip uninstall pyriksprot --yes  >& /dev/null ; \
		mv -f pyproject.tmp pyproject.toml ; \
		poetry update pyriksprot ; \
	fi

test: output-dir
	@poetry run pytest $(PYTEST_ARGS) tests
	@rm -rf ./tests/output/*

output-dir:
	@mkdir -p ./tests/output

retest:
	@poetry run pytest $(PYTEST_ARGS) --last-failed tests

init: tools
	@poetry install

info:
	@poetry run python -c 'import sysconfig; print(sysconfig.get_paths()["purelib"])'

.ONESHELL: guard-clean-working-repository
guard-clean-working-repository:
	@status="$$(git status --porcelain)"
	@if [[ "$$status" != "" ]]; then
		echo "error: changes exists, please commit or stash them: "
		echo "$$status"
		exit 65
	fi

version:
	@echo $(shell grep "^version \= " pyproject.toml | sed "s/version = //" | sed "s/\"//g")

tools:
	@pip install --upgrade pip --quiet
	@pip install poetry --upgrade --quiet
	@poetry run pip install --upgrade pip --quiet

.PHONY: sparv
sparv: tools
	@pipx install --upgrade https://github.com/spraakbanken/sparv-pipeline/archive/latest.tar.gz

bump.patch: requirements.txt
	@poetry version patch
	@git add pyproject.toml requirements.txt
	@git commit -m "📌 bump version patch"
	@git push

tag:
	@poetry build
	@git push
	@git tag $(shell grep "^version \= " pyproject.toml | sed "s/version = //" | sed "s/\"//g") -a
	@git push origin --tags

test-coverage:
	-poetry run coverage --rcfile=.coveragerc run -m pytest
	-poetry run coveralls

pytest:
	@mkdir -p ./tests/output
	@poetry run pytest --quiet tests

pylint:
	@poetry run pylint $(SOURCE_FOLDERS)

pylint2:
	@-find $(SOURCE_FOLDERS) -type f -name "*.py" | \
		grep -v .ipynb_checkpoints | \
			poetry run xargs -I @@ bash -c '{ echo "@@" ; pylint "@@" ; }'

mypy:
	@poetry run mypy --version
	@poetry run mypy .

flake8:
	@poetry run flake8 --version
	-poetry run flake8

isort:
	@poetry run isort --profile black --float-to-top --line-length 120 --py 38 $(SOURCE_FOLDERS)

black: clean-dev
	@poetry run black --version
	@poetry run black --line-length 120 --target-version py38 --skip-string-normalization $(SOURCE_FOLDERS)

clean-dev:
	@rm -rf .pytest_cache build dist .eggs *.egg-info
	@rm -rf .coverage coverage.xml htmlcov report.xml .tox
	@find . -type d -name '__pycache__' -exec rm -rf {} +
	@find . -type d -name '*pytest_cache*' -exec rm -rf {} +
	@find . -type d -name '.mypy_cache' -exec rm -rf {} +
	@rm -rf tests/output

clean-cache:
	@poetry cache clear pypi --all
	@poetry install --remove-untracked

update:
	@poetry update

requirements.txt: poetry.lock
	@poetry export --without-hashes -f requirements.txt --output requirements.txt

requirements.txt-to-git: requirements.txt
	@git add requirements.txt
	@git commit -m "📌 updated requirements.txt"
	@git push


snakemake-workflow:
	@cookiecutter gh:snakemake-workflows/cookiecutter-snakemake-workflow

gh:
	@sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-key C99B11DEB97541F0
	@sudo apt-add-repository https://cli.github.com/packages
	@sudo apt update && sudo apt install gh

check-gh: gh-exists
gh-exists: ; @which gh > /dev/null

.ONESHELL:
spacy-swedish-ups-models:
	@pushd . \
	&& cd /data \
	&& mkdir -p spacy \
	&& wget https://data.kb.se/datasets/2020/10/swedish_nlp/spacy/sv_model_upos.zip \
	&& unzip sv_model_upos.zip \
	&& rm -f sv_model_upos.zip \
	&& popd

.ONESHELL:
spacy-swedish-xps-models:
	@pushd . \
	&& cd /data \
	&& mkdir -p spacy \
	&& wget https://data.kb.se/datasets/2020/10/swedish_nlp/spacy/sv_model_xpos.zip \
	&& unzip sv_model_xpos.zip \
	&& rm -f sv_model_xpos.zip \
	&& popd


profile-tagging:
	@mkdir -p ./.profile-reports
	@poetry run python -m pyinstrument -r html -o ./.profile-reports/$(RUN_TIMESTAMP)_tagging-pyinstrument.html ./tests/profile_tagging.py

prepare-windows:
	@pyenv update
	@pyenv install 3.8.5
	@choco install make
	@mkdir sandbox
	@cd sandbox
	@pyenv local 3.8.5
	@python -m venv .venv
	@echo curl https://raw.githubusercontent.com/welfare-state-analytics/westac_parlaclarin_pipeline/main/Makefile > Makefile
	@pip install westac-parlaclarin-pipeline
	@mkdir C:\data
	@echo "INSTALL SPARV MODELS:"
	@echo "if git bash: DOS> mklink /d data C:\data"
	@SET SPARV_DATADIR=C:\data\sparv
	@cd $(SPARV_DATADIR)
	@git clone --depth 1 https://github.com/spraakbanken/sparv-models.git
	@mv sparv-models models
	@ln -s .venv/Lib/site-ackages/workflow workflow
	@ln -s .venv/Lib/site-ackages/scripts scripts



.PHONY: help check init version
.PHONY: lint flake8 pylint mypy black isort tidy
.PHONY: test retest test-coverage pytest
.PHONY: ready build tag bump.patch release fast-release
.PHONY: clean-dev clean-cache update
.PHONY: gh check-gh gh-exists tools

# # BERT_MODEL := bert-base-swedish-cased-ner
# BERT_MODEL := bert-base-swedish-cased-ner
# # BERT_MODEL := bert-base-swedish-cased-pos
# .PHONY: bert-models
# .ONESHELL:
# bert-models:
# 	@mkdir -p /data/swedish-bert-models/$(BERT_MODEL)
# 	@cd /data/swedish-bert-models/$(BERT_MODEL)
# 	@for filename in config.json vocab.txt pytorch_model.bin ; \
# 	do \
# 		wget https://s3.amazonaws.com/models.huggingface.co/bert/KB/$(BERT_MODEL)/$$filename ; \
# 	done

help: help-workflow
	@echo "Higher development level recepies: "
	@echo " make ready            Makes ready for release (tools tidy test flake8 pylint)"
	@echo " make build            Updates tools, requirement.txt and build dist/wheel"
	@echo " make release          Bumps version (patch), pushes to origin and creates a tag on origin"
	@echo " make fast-release     Same as release but without lint and test"
	@echo " make test             Runs tests with code coverage"
	@echo " make retest           Runs failed tests with code coverage"
	@echo " make lint             Runs pylint and flake8"
	@echo " make tidy             Runs black and isort"
	@echo " make clean-dev        Removes temporary files, caches, build files"
	@echo " make clean-cache      Clean poetry PyPI cache"
	@echo "  "
	@echo "Lower level recepies: "
	@echo " make init             Install development tools and dependencies (dev recepie)"
	@echo " make tag              bump.patch + creates a tag on origin"
	@echo " make bump.patch       Bumps version (patch), pushes to origin"
	@echo " make pytest           Runs teets without code coverage"
	@echo " make pylint           Runs pylint"
	@echo " make flake8           Runs flake8 (black, flake8-pytest-style, mccabe, naming, pycodestyle, pyflakes)"
	@echo " make isort            Runs isort"
	@echo " make black            Runs black"
	@echo " make gh               Installs Github CLI"
	@echo " make update           Updates dependencies"


stanza_models:
	@./scripts/stanza_models.sh
