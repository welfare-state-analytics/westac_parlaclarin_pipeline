#!/bin/bash

. .env

TARGET_FOLDER=/data/riksdagen_corpus_data/v0.10.0/tagged_frames

# In Bash, loop over folder in TARGET_FOLDER
for folder in $TARGET_FOLDER/*; do
    if [ ! -d "$folder" ]; then
        continue
    fi
    subfolder=$(basename $folder)
    if [ -d "$folder/$subfolder" ]; then
        echo "Duplicate folder layer found: $folder/$subfolder"
        mv $folder/$subfolder/* $folder
        rm -r $folder/$subfolder
    fi
done
