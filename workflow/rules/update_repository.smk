# type: ignore
# pylint: skip-file, disable-all
import os
from workflow.config import Config

config: Config = config


rule init_repository:
    log:
        LOG_NAME,
    message:
        "step: create shallow copy of ParlaClarin repository"
    output:
        directory(config.parla_clarin.repository_folder),
    log:
        "init_repository.log",
    shell:
        f"""
           pushd . \
        && cd {config.parla_clarin.repository_parent_folder} \
        && git clone --depth 1 {config.parla_clarin.repository_url} \
        && git config core.quotepath off \
        && popd
        """


rule update_repository:
    log:
        LOG_NAME,
    message:
        "step: do a shallow update of ParlaClarin repository"
    shell:
        f"""\
           pushd . \
        && cd {config.parla_clarin.repository_folder} \
        && git fetch --depth 1 \
        && git reset --hard origin \
        && git clean -dfx \
        && git config core.quotepath off \
        && popd \
        """


rule update_repository_timestamps:
    log:
        LOG_NAME,
    message:
        "step: sets timestamp of repository files to last commit"
    shell:
        """
        {PACKAGE_PATH}/scripts/git_update_mtime.sh {config.parla_clarin.repository_folder}
        """


rule sync_deleted_files:
    log:
        LOG_NAME,
    run:
        utility.sync_delta_names(
            config.parla_clarin.source_folder, "xml", config.extract_speeches.folder, "txt", delete=True
        )
