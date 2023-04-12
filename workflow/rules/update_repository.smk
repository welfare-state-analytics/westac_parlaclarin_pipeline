# type: ignore
# pylint: skip-file, disable-all
import os

repository_name = os.path.basename(typed_config.source.repository_folder)


rule init_repository:
    log:
        typed_config.log_filename,
    message:
        "step: create shallow copy of ParlaClarin repository"
    output:
        directory(typed_config.source.repository_folder),
    log:
        "init_repository.log",
    shell:
        f"""
           pushd . \
        && cd {typed_config.source.parent_folder} \
        && git clone --branch {typed_config.source.repository_tag} --depth 1 {typed_config.source.repository_url} \
        && cd {repository_name} \
        && git config core.quotepath off \
        && popd
        """


rule update_repository:
    log:
        typed_config.log_filename,
    message:
        "step: do a shallow update of ParlaClarin repository"
    shell:
        f"""\
           pushd . \
        && cd {typed_config.source.repository_folder} \
        && git fetch --depth 1 \
        && git reset --hard origin \
        && git clean -dfx \
        && git config core.quotepath off \
        && popd \
        """


rule update_repository_timestamps:
    # log:
    #     typed_config.log_filename,
    message:
        "step: sets timestamp of repository files to last commit"
    shell:
        """
        {PACKAGE_PATH}/scripts/git_update_mtime.sh {typed_config.source.repository_folder}
        """


rule sync_deleted_files:
    # log:
    #     typed_config.log_filename,
    run:
        utility.sync_delta_names(typed_config.source.folder, "xml", typed_config.target.folder, "zip", delete=True)
        # utility.sync_delta_names(
        #     typed_config.source.folder, "xml", typed_config.extract.folder, "txt", delete=True
        # )

