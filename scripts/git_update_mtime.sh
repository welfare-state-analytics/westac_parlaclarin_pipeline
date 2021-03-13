#!/bin/bash
# See https://snakemake.readthedocs.io/en/stable/project_info/faq.html#git-is-messing-up-the-modification-times-of-my-input-files-what-can-i-do

git_folder=

usage_message=$(cat <<EOF
usage: git_update_mtime GIT_FOLDER
EOF
)

if [  $# != 1 ]; then
    echo $usage_message
    exit 64
fi

git_folder=$1

if [ ! -d "$git_folder" ] ; then
    echo "error: not such folder $git_folder"
    exit 64
fi

if [ ! -d "${git_folder}/.git" ] ; then
    echo "error: not a git repository $git_folder"
    exit 64
fi

git_sync_mtime(){
    local f
    for f; do
        #current_time=`git log --pretty=%at -n1 -- "$f"`
        #echo "$f: $current_time"
        touch -d @0`git log --pretty=%at -n1 -- "$f"` "$f"
    done
}

git_sync_mtimes(){
    for f in $(git ls-tree -r $(git rev-parse --abbrev-ref HEAD) --name-only); do
        git_sync_mtime "$f"
    done
}

pushd .
cd ${git_folder} && git_sync_mtimes
popd
