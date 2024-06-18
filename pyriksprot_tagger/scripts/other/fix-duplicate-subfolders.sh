#!/bin/bash

. .env

# TARGET_FOLDER=/data/riksdagen_corpus_data/v0.10.0/corpus/tagged_frames
TARGET_FOLDER=/data/riksdagen_corpus_data/corpus/v0.10.0/tagged_frames

# In Bash, loop over folder in TARGET_FOLDER
for folder in $TARGET_FOLDER/*; do
    if [ ! -d "$folder" ]; then
        continue
    fi
    subfolder=$(basename $folder)
    if [ -d "$folder/$subfolder" ]; then
        echo "Duplicate folder layer found: $folder/$subfolder"
        mv $folder/$subfolder/* $folder
        rmdir $folder/$subfolder
    fi
done
