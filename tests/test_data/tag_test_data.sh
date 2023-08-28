#!/bin/bash

. .env

echo
import pyriksprot_tagger.utility as pu\n

pu.tag_test_data("tests/test_data/source", "${RIKSPROT_REPOSITORY_TAG=}")
EOF | python
