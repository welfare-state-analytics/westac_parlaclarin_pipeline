# This file implements a Github Parla-Clarin to tagged text pipeline
################################################################################
#                               CONFIGURATION                                  #
################################################################################

.DEFAULT_GOAL=lint

REQUIRED_TOOLS					:= java
SHELL 							:= /bin/bash
XSLT_PROCESSOR					:= saxon
#XSLT_PROCESSOR					:= java net.sf.saxon.Transform -s:source -xsl:stylesheet -o:output

ROOT_FOLDER 					:= /data/riksdagen_corpus_data

REPOSITORY_NAME 				:= riksdagen-corpus
SOURCE_PARLA_CLARIN_DATA_FOLDER := $(ROOT_FOLDER)/$(REPOSITORY_NAME)/data/new-parlaclarin
TARGET_EXPORT_FOLDER 			:= $(ROOT_FOLDER)/$(REPOSITORY_NAME)-exports

SOURCE_REPOSITORY_URL 			:= https://github.com/welfare-state-analytics/$(REPOSITORY_NAME).git

# GIT_BRANCH  := $(shell git rev-parse --abbrev-ref HEAD)
# GIT_SHA     := $(shell git rev-parse HEAD)
# BUILD_DATE  := $(shell date -u +"%Y-%m-%dT%H:%M:%SZ")

PARLA_CLARIN_TEXT_FOLDER = $(TARGET_EXPORT_FOLDER)/parla_clarin_text
PARLA_CLARIN_XML_FILES = $(wildcard $(SOURCE_PARLA_CLARIN_DATA_FOLDER)/*.xml)
PARLA_CLARIN_TEXT_FILES = $(patsubst $(SOURCE_PARLA_CLARIN_DATA_FOLDER)/%.xml,$(PARLA_CLARIN_TEXT_FOLDER)/%.txt,$(PARLA_CLARIN_XML_FILES))
PARLA_CLARIN_TO_TEXT_XSLT = parlaclarin_xml_to_csv.xslt
PARLA_CLARIN_TEXT_ZIP = $(PARLA_CLARIN_TEXT_FOLDER)/$(REPOSITORY_NAME).txt.zip

SAXON_JAR = ../resources/lib/saxon-he.jar

# define xslt_process
# 	ifeq ($(XSLT_PROCESSOR),saxon)
# 		java -jar=lib/saxon-he.jar net.sf.saxon.Transform -s:$1 -xsl:$(PARLA_CLARIN_TO_TEXT_XSLT) -o:$2
# 	else
# 		xsltproc --output $2 $(PARLA_CLARIN_TO_TEXT_XSLT) $1
# 	endif
# endef

################################################################################
#                                MISC CHECKS                                   #
################################################################################

 ifeq (, $(shell which java))
   $(error "no java in PATH")
 endif

################################################################################
#                                  RULES                                       #
################################################################################


# ifeq ($(PYTHONPATH),)
#   $(error Environment variable 'PYTHONPATH' not set)
# endif

# Configure GNU make to remove files when error occurred
.DELETE_ON_ERROR:

# Stop GNU make from removing intermediate files:
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
init: $(TARGET_EXPORT_FOLDER) $(PARLA_CLARIN_TEXT_FOLDER) $(ROOT_FOLDER)/$(REPOSITORY_NAME)
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
update_parla_clarin_xml:
	@echo "update_parla_clarin_xml"
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

.PHONY: help clean init update_parla_clarin_xml parla_clarin_to_text

parla_clarin_to_text: $(PARLA_CLARIN_TEXT_FILES)
	@echo "step[parla_clarin --> text]: done"

$(PARLA_CLARIN_TEXT_FOLDER)/%.txt : $(SOURCE_PARLA_CLARIN_DATA_FOLDER)/%.xml
	@mkdir -p $(PARLA_CLARIN_TEXT_FOLDER)
	#@xsltproc --output $(PARLA_CLARIN_TEXT_FOLDER)/$(notdir $@) $(PARLA_CLARIN_TO_TEXT_XSLT) $<
	java -jar $(SAXON_JAR) $< $(PARLA_CLARIN_TO_TEXT_XSLT) > $(PARLA_CLARIN_TEXT_FOLDER)/$(notdir $@)
	#@zip -jom $(PARLA_CLARIN_TEXT_ZIP) $(PARLA_CLARIN_TEXT_FOLDER)/$(notdir $@)
	#@touch $@

help:
	@echo "Lower level recepies: "
	@echo " make init             Install development tools and dependencies (dev recepie)"
	@echo " make help             Display this message"
	@echo "  "


$(SAXON_JAR):
	@wget https://sourceforge.net/projects/saxon/files/latest/download
	@mkdir -p ./saxon_temp && mv download ./saxon_temp/SaxonHE.zip && cd ./saxon_temp
	@unzip SaxonHE.zip
	@rm -rf *test*.jar jline*.jar *xqj*.jar
	@mv -f saxon-he-*.jar $(SAXON_JAR)
	@cd .. && rm-rf ./saxon_temp
