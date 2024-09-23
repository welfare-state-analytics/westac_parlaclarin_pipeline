#!/bin/bash

. tests/test.env

if [ -z "$CONFIG_FILENAME" ]; then
  echo "CONFIG_FILENAME is not set"
  exit 1
fi

VERSION=$(yq '.corpus.version' ${CONFIG_FILENAME})
INPUT_FOLDER=$(yq '.corpus.folder' ${CONFIG_FILENAME})
WORD_FREQUENCY_FILENAME=$(yq '.dehyphen.tf_filename' ${CONFIG_FILENAME})

if [ -f "${WORD_FREQUENCY_FILENAME}" ]; then
  echo "warning: TF file ${WORD_FREQUENCY_FILENAME} not found."
  echo "info: using riksprot2tfs to create ${WORD_FREQUENCY_FILENAME}"
  riksprot2tfs ${INPUT_FOLDER} ${WORD_FREQUENCY_FILENAME}
fi


PYTHONPATH=. poetry run python -c "
import tests.utility as pu; 
pu.pos_tag_testdata_for_current_version('${CONFIG_FILENAME}', force=True)
"
