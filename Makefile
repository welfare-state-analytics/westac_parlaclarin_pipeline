.DEFAULT_GOAL=lint

include ./workflow/Makefile

SHELL := /bin/bash
SOURCE_FOLDERS=workflow tests
PACKAGE_FOLDER=workflow
PYTEST_ARGS=--durations=0 --cov=$(PACKAGE_FOLDER) --cov-report=xml --cov-report=html tests


optional_executables = dot
K := $(foreach exec,$(EXECUTABLES),\
        $(if $(shell which $(exec)),some string,$(error "No $(exec) in PATH")))

fast-release: clean tidy build guard_clean_working_repository bump.patch tag

release: ready guard_clean_working_repository bump.patch tag

#gh release create v0.2.35 --title "Release" --notes ""

ready: tools clean tidy test lint build

build: requirements.txt
	@poetry build

.ONESHELL:
development_install:
	@poetry build --quiet
	@dist_tarball=$$(basename `ls -1b dist/westac_parlaclarin_pipeline*.tar.gz`)
	@filename="$${dist_tarball%.*}"
	@filename="$${filename%.*}"
	@tar -zxvf dist/$$dist_tarball -C . $$filename/setup.py
	@if [ -f $$filename/setup.py ] ; then \
		mv -f $$filename/setup.py . ; \
		rm -rf $$filename ; \
	 fi
	@poetry run pip install -e .


lint: tidy pylint

snakelint:
	-poetry run snakemake --lint

snakefmt:
	@snakefmt --exclude *.py $(PACKAGE_FOLDER)

.PHONY: snaketab
snaketab:
	@snakemake --bash-completion

#tidy: black isort snakefmt
tidy: black isort

test:
	@mkdir -p ./tests/output
	@poetry run pytest $(PYTEST_ARGS) tests
	@rm -rf ./tests/output/*

retest:
	@poetry run pytest $(PYTEST_ARGS) --last-failed tests

init: tools
	@poetry install


.ONESHELL: guard_clean_working_repository
guard_clean_working_repository:
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
	@poetry add cookiecutter

.PHONY: sparv
sparv: tools
	@pipx install --upgrade https://github.com/spraakbanken/sparv-pipeline/archive/latest.tar.gz

bump.patch: requirements.txt
	@poetry run dephell project bump patch
	@git add pyproject.toml requirements.txt
	@git commit -m "Bump version patch"
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

black: clean
	@poetry run black --version
	@poetry run black --line-length 120 --target-version py38 --skip-string-normalization $(SOURCE_FOLDERS)

clean:
	@rm -rf .pytest_cache build dist .eggs *.egg-info
	@rm -rf .coverage coverage.xml htmlcov report.xml .tox
	@find . -type d -name '__pycache__' -exec rm -rf {} +
	@find . -type d -name '*pytest_cache*' -exec rm -rf {} +
	@find . -type d -name '.mypy_cache' -exec rm -rf {} +
	@rm -rf tests/output

clean-cache:
	@poetry cache clear pypi --all

update:
	@poetry update

snakemake-workflow:
	@cookiecutter gh:snakemake-workflows/cookiecutter-snakemake-workflow

gh:
	@sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-key C99B11DEB97541F0
	@sudo apt-add-repository https://cli.github.com/packages
	@sudo apt update && sudo apt install gh

requirements.txt: poetry.lock
	@poetry export -f requirements.txt --output requirements.txt

check-gh: gh-exists
gh-exists: ; @which gh > /dev/null

.PHONY: help check init version
.PHONY: lint flake8 pylint mypy black isort tidy
.PHONY: test retest test-coverage pytest
.PHONY: ready build tag bump.patch release fast-release
.PHONY: clean clean_cache update
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
	@echo " make clean            Removes temporary files, caches, build files"
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
