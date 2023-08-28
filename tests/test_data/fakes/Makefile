include .env

SHELL := /bin/bash

DATA_FOLDER=.
TAGGER_CONFIG_FILENAME=opts/tagger-config.yml
SOURCE_FOLDER=$(shell yq '.source.folder' opts/tagger-config.yml)

dataset: parlaclarin-corpus word-frequencies tag-protocols tagged-speech-corpora text-corpora dtm-corpora

parlaclarin-corpus:
	@echo "corpus exists

# @echo "Target(s): 1) subset of Parla-CLARIN corpus 2) processed metadata"
# @echo "Script(s): pyriksprot.scripts.subset-corpus:main"
# @subset-corpus ./protocols.txt ./ $(SWEDEB_TAG)

tools: ~/bin/yq
	@echo "Check(s): yq is installed"

~/bin/yq:
	@wget https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64 -O ~/bin/yq
	@chmod +x ~/bin/yq

word-frequencies:
	@echo "Target(s): global term frequencies (TF)"
	@echo "Script(s): pyriksprot.scripts.riksprot2tfs:main"
	@mkdir -p $(SWEDEB_TAG)/dehyphen_datadir
	@riksprot2tfs $(SWEDEB_TAG)/parlaclarin $(SWEDEB_TAG)/dehyphen_datadir/word-frequencies.pkl

tag-protocols: tools
	@echo "`date '+%Y-%m-%d %T.%3N'` | INFO     | Target(s): tagged parlaclarin protocols (tagged frames)"
	@echo "`date '+%Y-%m-%d %T.%3N'` | INFO     | Script(s): pyriksprot_tagger.scripts.tag:main"
	@echo "`date '+%Y-%m-%d %T.%3N'` | INFO     | Looking for source files in $(SOURCE_FOLDER)"
	@pos_tag --force --recursive $(TAGGER_CONFIG_FILENAME) $(SOURCE_FOLDER) $(SWEDEB_TAG)/tagged_frames
	@cp -f $(SWEDEB_TAG)/tagged_frames/prot-*.zip ../../../../pyriksprot/tests/test_data/fakes/v0.6.0/tagged_frames/

tagged-speech-corpora: ./opts/tagged-speeches/*.yml
	@echo "Target(s): tagged speech corpora (tagged frames)"
	@echo "Script(s): pyriksprot.scripts.riksprot2speech:main"
	@rm -rf $(SWEDEB_TAG)/speeches && mkdir -p $(SWEDEB_TAG)/speeches
	@for file in $^ ; do \
		echo " => $(SWEDEB_TAG)/speeches/$$(basename $${file%.yml})" ; \
		riksprot2speech \
			--options-filename $${file} --force \
			$(SWEDEB_TAG)/tagged_frames \
				$(SWEDEB_TAG)/riksprot_metadata.db \
					$(SWEDEB_TAG)/speeches/$$(basename $${file%.yml}) ; \
    done

text-corpora: ./opts/plain-text-speeches/*.yml
	@echo "Target(s): speech text corpora (plain text)"
	@echo "Script(s): pyriksprot.scripts.riksprot2speech_text:main"
	@mkdir -p $(SWEDEB_TAG)/speeches
	@for file in $^ ; do \
		echo " => $(SWEDEB_TAG)/speeches/$$(basename $${file%.yml})" ; \
		riksprot2speech_text \
			--options-filename $${file} --force \
			$(SWEDEB_TAG)/parlaclarin/protocols \
				$(SWEDEB_TAG)/riksprot_metadata.db \
					$(SWEDEB_TAG)/speeches/$$(basename $${file%.yml}).zip ; \
    done

PENELOPE_FOLDER=/home/roger/source/penelope
dtm-corpora: ./opts/dtm/*.yml
	@echo "Target(s): DTM corpora"
	@echo "Script(s): pyriksprot.scripts.riksprot2speech_text:main"
	@echo "     Note: penelope must be installed in current environment"
	@rm -rf $(SWEDEB_TAG)/dtm && mkdir -p $(SWEDEB_TAG)/dtm
	 for file in $^ ; do \
	 	tag=$$(basename $${file%.yml})
		echo " => $(SWEDEB_TAG)/speeches/$${tag}" ; \
		vectorize-id \
		    --create-subfolder \
			--options-filename $${file} \
			--corpus-source $(SWEDEB_TAG)/speeches/tagged_frames_speeches_$${tag}.feather \
			--output-folder $(SWEDEB_TAG)/dtm \
			--output-tag $${tag} ; \
    done
# poetry run -C $(PENELOPE_FOLDER) vectorize-id \

clean:
	@rm -rf $(SWEDEB_TAG)
