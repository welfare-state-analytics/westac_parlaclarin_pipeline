#!/bin/bash
export OMP_NUM_THREADS=16
export PYTHONPATH=.

source .env

data_folder=${RIKSPROT_DATA_FOLDER}
target_folder=
source_pattern="*"
tag=${RIKSPROT_REPOSITORY_TAG}
force=0
update=1
max_procs=1
now_timestamp=$(date "+%Y%m%d_%H%M%S")
log_dir=./logs
scriptname=$(basename $0)

function usage()
{
    echo "usage: ./${scriptname} [--data-folder folder] [--source-pattern pattern] --target-folder folder --tag tag [--force] [--update] [--max-procs n]]"
    echo "Creates new database using source as template. Source defaults to production."
    echo ""
    echo "   --data-folder             source root folder"
    echo "   --source-pattern          source folder pattern"
    echo "   --target-folder           target folder"
    echo "   --tag                     source corpus tag"
    echo "   --force                   drop target if exists"
    echo "   --update                  update target if exists"
    echo "   --max-procs               max number of parallel jobs"
    echo ""
}

POSITIONAL=()
while [[ $# -gt 0 ]]
do
    key="$1"
    case $key in
        --source-pattern)
            source_pattern="$2"; shift; shift
        ;;
        --tag)
            tag="$2"; shift; shift
        ;;
        --data-folder)
            data_folder="$2"; shift; shift
        ;;
        --target-folder)
            target_folder="$2"; shift; shift
        ;;
        --max-procs)
            max_procs="$2"; shift; shift
        ;;
        --force)
            force=1 ;
        ;;
        --update)
            update=1 ;
        ;;
        --help)
            usage ;
            exit 0
        ;;
        *)
        POSITIONAL+=("$1")
        shift
        ;;
    esac
done

set -- "${POSITIONAL[@]}"

if [ "$data_folder" == "" ]; then
    usage
    exit 64
fi

if [ ! -d "$data_folder" ]; then
    echo "error: data folder doesn't exist"
    usage
    exit 64
fi

if [ "$tag" == "" ]; then
    echo "error: tag not specified" ;
    usage
    exit 64
fi

if [ "$target_folder" == "" ]; then
    echo "error: target folder not specified" ;
    usage
    exit 64
fi

if [ -d "$target_folder" ]; then
    if [ $force == 1 ]; then
        echo "info: dropping existing target" ;
        echo rm -rf $target_folder ;
    elif [ $update == 0 ]; then
        echo "error: target folder exists (use --force or --update to remove/update existing tagging)" ;
        exit 64 ;
    fi
fi

if [[ $max_procs < 1 || $max_procs > 6 ]]; then
    echo "error: max procs bust be an integer between 1 and 6" ;
    exit 64
fi

repository_folder=${data_folder}/riksdagen-corpus
corpus_folder=${repository_folder}/corpus/protocols


workdir_tag=undefined
if command -v "$tag_info" > /dev/null; then
    workdir_tag=$(tag_info --key tag ${repository_folder})
elif [ -f "pyriksprot_tagger/scripts/tag_info.py" ]; then
    export PYTHONPATH=.
    workdir_tag=$(poetry run python pyriksprot_tagger/scripts/tag_info.py --key tag ${repository_folder})
else

    tag_info_filename=$(python - "$input" <<'END_SCRIPT'
import pyriksprot_tagger, os
print(os.path.join(os.path.dirname(pyriksprot_tagger.__file__), "scripts/tag_info.py"))
END_SCRIPT
)

    if [ -f "$tag_info_filename" ]; then
        workdir_tag=$(poetry run python ${tag_info_filename} --key tag ${repository_folder})
    else

        echo "error: tag_info not found - unable to verify that workdir tag id ${tag}"
        exit 64 ;
    fi
fi

if [ "$tag" != "$workdir_tag" ]; then
    echo "error: workdir tag is $workdir_tag, expected ${tag}" ;
    exit 64 ;
fi

mkdir -p ${target_folder} ${log_dir}
tag_info $repository_folder > ${target_folder}/version.yml

sub_folders=`find ${corpus_folder} -maxdepth 1 -mindepth 1 -name "${source_pattern}" -type d -printf '%f\n' | sort`

yaml_file=$log_dir/tag_config_${now_timestamp}.yml

cat <<EOF > $yaml_file
root_folder: ${data_folder}
source:
    folder: ${corpus_folder}
    repository_folder: ${repository_folder}
    repository_tag: ${tag}
target:
    folder: ${target_folder}
dehyphen:
  folder: /data/riksdagen_corpus_data/dehyphen
  tf_filename: /data/riksdagen_corpus_data/metadata/${tag}/word-frequencies.pkl
tagger:
  module: pyriksprot_tagger.taggers.stanza_tagger
  stanza_datadir: ${STANZA_DATADIR}
  preprocessors: dedent,dehyphen,strip,pretokenize
  lang: "sv"
  processors: tokenize,lemma,pos
  tokenize_pretokenized: true
  tokenize_no_ssplit: true
  use_gpu: true
  num_threads: 1
EOF
echo "info: using configuration file $yaml_file"
cp $yaml_file ${target_folder}/tag_config.yml

echo "info: using $max_procs processes"
echo "info: running in $force force mode"

# if [ ! command -v "pos_tag" > /dev/null ]; then
#     echo "error: pos_tag command not found - unable to run tagging"
#     echo " info: install the `pyriksprot_tagger` package and make sure that the pos_tag command is available"
#     exit 64 ;
# fi

if [[ $max_procs > 1 ]]; then

    tag_command_file="$log_dir/tag_commands_${now_timestamp}.txt"

    echo "command file: $tag_command_file"

    rm -rf $tag_command_file

    for sub_folder in $sub_folders; do
        echo "poetry run python ./pyriksprot_tagger/scripts/tag.py $yaml_file ${corpus_folder}/$sub_folder ${target_folder}/$sub_folder" >> ${tag_command_file}
        # echo "pos_tag  $yaml_file ${corpus_folder}/$sub_folder ${target_folder}/$sub_folder" >> ${tag_command_file}
    done

    echo "info: running in parallel mode using $max_procs processes"
    cat $tag_command_file | xargs -I CMD --max-procs=$max_procs bash -c CMD

else
    echo "info: running in sequential mode"
    for sub_folder in $sub_folders; do
        PYTHONPATH=. python ./pyriksprot_tagger/scripts/tag.py $yaml_file ${corpus_folder}/$sub_folder ${target_folder}/$sub_folder
        # PYTHONPATH=. pos_tag $yaml_file ${corpus_folder}/$sub_folder ${target_folder}/$sub_folder 
    done
fi
