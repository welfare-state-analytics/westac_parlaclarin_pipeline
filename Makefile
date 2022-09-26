include .env

include ./Makefile.dev

DATA_FOLDER=/data/riksdagen_corpus_data

start-pos-tag:
	@nohup poetry run ./tag-it.sh --data-folder $(DATA_FOLDER) --tag $(RIKSPROT_REPOSITORY_TAG) --max-procs 4 --target-folder $(DATA_FOLDER)/tagged_frames_$(TAG) &

# echo "usage: tag-it [--data-folder folder] [--source-pattern pattern] --target-folder folder --tag tag [--force]"
# echo "Creates new database using source as template. Source defaults to production."
# echo ""
# echo "   --data-folder             source root folder"
# echo "   --target-folder           target folder"
# echo "   --tag                     source corpus tag"
# echo "   --source-pattern          source folder pattern"
# echo "   --force                   drop target if exists"
# echo "   --update                  update target if exists"
# echo "   --max-procs               max number of parallel jobs"
# echo ""
