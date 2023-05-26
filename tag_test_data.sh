#!/bin/bash

. .env

PYTHONPATH=. poetry run python -c "
import tests.utility as pu; 
pu.tag_test_data('tests/test_data/source', '${RIKSPROT_REPOSITORY_TAG}')
"
