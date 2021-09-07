# type: ignore
# pylint: skip-file, disable-all
import os
from workflow.config import Config

repository_name = os.path.basename(typed_config.parla_clarin.repository_folder)


rule init_repository:
    log:
        typed_config.log_path,
    message:
        "step: create shallow copy of ParlaClarin repository"
    output:
        directory(typed_config.parla_clarin.repository_folder),
    log:
        "init_repository.log",
    shell:
        f"""
           pushd . \
        && cd {typed_config.parla_clarin.repository_parent_folder} \
        && git clone --branch {typed_config.parla_clarin.repository_branch} --depth 1 {typed_config.parla_clarin.repository_url} \
        && cd {repository_name} \
        && git config core.quotepath off \
        && popd
        """


rule update_repository:
    log:
        typed_config.log_path,
    message:
        "step: do a shallow update of ParlaClarin repository"
    shell:
        f"""\
           pushd . \
        && cd {typed_config.parla_clarin.repository_folder} \
        && git fetch --depth 1 \
        && git reset --hard origin \
        && git clean -dfx \
        && git config core.quotepath off \
        && popd \
        """


rule update_repository_timestamps:
    # log:
    #     typed_config.log_path,
    message:
        "step: sets timestamp of repository files to last commit"
    shell:
        """
        {PACKAGE_PATH}/scripts/git_update_mtime.sh {typed_config.parla_clarin.repository_folder}
        """


rule sync_deleted_files:
    # log:
    #     typed_config.log_path,
    run:
        utility.sync_delta_names(typed_config.parla_clarin.source_folder, "xml", typed_config.annotated_folder, "zip", delete=True)
        # utility.sync_delta_names(
        #     typed_config.parla_clarin.source_folder, "xml", typed_config.extract_speeches.folder, "txt", delete=True
        # )

