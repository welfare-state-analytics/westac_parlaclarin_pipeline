include .env

include ./Makefile.dev
log_file=$(date "+%Y%m%d%H%M%S"`_"deploy_${target_db_name}_${source_type}.log)

.PHONY: tag-it
tag-it:
	@nohup poetry run ./tag.sh --data-folder $(RIKSPROT_DATA_FOLDER) \
		--tag $(RIKSPROT_REPOSITORY_TAG) --max-procs 4 \
		--target-folder $(RIKSPROT_DATA_FOLDER)/$(RIKSPROT_REPOSITORY_TAG)/tagged_frames >> tag-it-$(RIKSPROT_REPOSITORY_TAG).nohup.log &

tag_test_cmd := import tests.utility as pu; pu.tag_test_data('tests/test_data/source', '$(RIKSPROT_REPOSITORY_TAG)')
tag-test-data:
	@PYTHONPATH=. poetry run python -c "$(tag_test_cmd)"

vrt-test-data:
	@PYTHONPATH=. poetry run riksprot2vrt \
		--source-folder tests/test_data/source/$(RIKSPROT_REPOSITORY_TAG)/tagged_frames/ \
			--target-folder tests/test_data/source/$(RIKSPROT_REPOSITORY_TAG)/vrt/ -t protocol -t speech --batch-tag year

.PHONY: cwb
cwb:
	cwb-encode -d tests/output/cwb

.PHONY: image
image:
	@docker build \
		-t pyriksprot:latest -t pyriksprot:$(RIKSPROT_REPOSITORY_TAG) \
		--build-arg PACKAGE_VERSION=$(PACKAGE_VERSION) .

.PHONY: bash
bash:
	@docker run --gpus all -it --rm \
		--mount "type=bind,src=$(shell pwd),dst=/home/pyriksprot/work" \
		--mount "type=bind,src=/data,dst=/data" pyriksprot:latest /bin/bash
