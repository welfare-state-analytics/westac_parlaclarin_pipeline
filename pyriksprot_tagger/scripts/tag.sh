#!/bin/bash
export OMP_NUM_THREADS=16
export PYTHONPATH=.

source .env

root_folder=
corpus_folder=
target_folder=
source_pattern="*"
tag=
force=no
update=1
max_procs=1
now_timestamp=$(date "+%Y%m%d_%H%M%S")
log_dir=./logs
scriptname=$(basename $0)
repository_name=riksdagen-records

function usage()
{
    if [ "$1" != "" ]; then
        echo "error: $1"
    fi
    echo "usage: ./${scriptname} [--root-folder folder]  [--corpus-folder folder] --target-folder folder --tag tag [--force] [--update] [--max-procs n]]"
    echo "Tags XML files found in corpus folder and its subfolders."
    echo ""
    echo "   --root-folder             root data and metadata folder (dehyphen, models, TF etc.)"
    echo "   --corpus-folder           source corpus folder"
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
        --tag)
            tag="$2"; shift; shift
        ;;
        --root-folder|--data-folder)
            root_folder="$2"; shift; shift
        ;;
        --corpus-folder)
            corpus_folder="$2"; shift; shift
        ;;
        --source-pattern)
            source_pattern="$2"; shift; shift
        ;;
        --target-folder)
            target_folder="$2"; shift; shift
        ;;
        --max-procs)
            max_procs="$2"; shift; shift
        ;;
        --force)
            force=yes ;
        ;;
        --update)
            update=1 ;
        ;;
        --help)
            usage ;
            exit 0
        ;;
        --*)
            usage "unknown option $1" ;
            exit 0
        ;;
        *)
        POSITIONAL+=("$1")
        shift
        ;;
    esac
done

set -- "${POSITIONAL[@]}"

if [ "$root_folder" == "" ]; then
    usage "root folder not specified"
    exit 64
fi

if [ ! -d "$root_folder" ]; then
    usage "data folder doesn't exist"
    exit 64
fi

if [ "$corpus_folder" == "" ]; then
    usage "source corpus folder not specified"
    exit 64
fi

if [ "$tag" == "" ]; then
    usage "tag not specified"
    exit 64
fi

if [ ! -d "$corpus_folder" ]; then
    usage  "corpus folder doesn't exist"
    exit 64
fi

if [ "$target_folder" == "" ]; then
    usage "target folder not specified" ;
    exit 64
fi

if [ -d "$target_folder" ]; then
    if [ "$force" == "yes" ]; then
        echo "info: running in force mode, dropping existing target" ;
        echo rm -rf $target_folder ;
    elif [ $update == 0 ]; then
        echo "error: target folder exists (use --force or --update to remove/update existing tagging)" ;
        exit 64 ;
    fi
fi

if [[ $max_procs < 1 || $max_procs > 6 ]]; then
    echo "error: max procs must be an integer between 1 and 6" ;
    exit 64
fi

word_frequency_filename=${root_folder}/${tag}/dehyphen/word-frequencies.pkl

mkdir -p ${target_folder} ${log_dir}

pushd "$corpus_folder" > /dev/null || exit 1
repository_folder=$(git rev-parse --show-toplevel 2> /dev/null || echo "")
popd > /dev/null

if ! expr "${corpus_folder}" : ".*${repository_name}$" > /dev/null; then
    echo "info: repository folder is ${repository_folder}, skipping tags check..." ;
    repository_folder="" ;
else
    echo "info: repository folder is ${repository_folder}, checking that tags match..." ;
fi

if [ "$repository_folder" != "" ]; then

    workdir_tag=undefined
    if command -v "$tag_info" > /dev/null; then
        workdir_tag=$(tag_info --key tag ${corpus_folder})
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
 bfa    
            echo "error: tag_info not found - unable to verify that workdir tag id ${tag}"
            exit 64 ;
        fi
    fi

    if [ "$tag" != "$workdir_tag" ]; then
        echo "error: workdir tag is $workdir_tag, expected ${tag}" ;
        exit 64 ;
    fi

    tag_info $repository_folder > ${target_folder}/version.yml

fi

echo $tag > ${target_folder}/version

sub_folders=`find ${corpus_folder} -maxdepth 1 -mindepth 1 -name "${source_pattern}" -type d -printf '%f\n' | sort`

yaml_file=$log_dir/tag_config_${now_timestamp}.yml

echo "info: tag: $tag"
echo "info: force: $force"
echo "info: root folder: $root_folder"
echo "info: corpus folder: $corpus_folder"
echo "info: target folder: $target_folder"
echo "info: word frequency filename: $word_frequency_filename"

cat <<EOF > $yaml_file
root_folder: ${root_folder}
data_folder: ${root_folder}
version: ${tag}

corpus:
  version: ${tag}
  folder: ${corpus_folder}
  pattern: "**/prot-*-*.xml"
  github:
    user: swerik-project
    repository: ${repository_name}
    path: data
    local_folder: ${repository_folder}

metadata:
  version: ${tag}
  folder: ${root_folder}/metadata/${tag}
  database:
    type: pyriksprot.metadata.database.SqliteDatabase
    options:
      filename: ${root_folder}/metadata/riksprot_metadata.${tag}.db
  github:
    user: swerik-project
    repository: riksdagen-persons
    path: data

tagged_frames:
  folder: ${target_folder}
  file_pattern: "prot-*.zip"
  pattern: ${root_folder}/${tag}/tagged_frames/**/prot-*.zip

tagged_speeches:
  folder: ${root_folder}/${tag}/tagged_frames_speeches.feather

dehyphen:
  folder: ${root_folder}/dehyphen
  tf_filename: ${root_folder}/${tag}/dehyphen/word-frequencies.pkl
  
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
if [ -f "${word_frequency_filename}" ]; then
    if [ "$force" == "yes" ]; then
        echo "info: force mode, dropping existing word frequency file: ${word_frequency_filename}"
        rm -f ${word_frequency_filename}
    else
        echo "info: word frequency file exists: ${word_frequency_filename}"
    fi

fi

if [ ! -f "${word_frequency_filename}" ]; then
    echo "info: generating word frequency file ${word_frequency_filename}..."
    riksprot2tfs $yaml_file
fi

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
