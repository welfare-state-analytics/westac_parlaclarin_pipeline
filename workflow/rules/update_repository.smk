# type: ignore
# pylint: skip-file, disable-all
import os
from workflow.config.typed_config import Config

config: Config = config

# FIXME #4 Only create shallow, nopn-updateable clones of repository
rule init_repository:
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


# FIXME #3 Unicode filennames are ASCII-encoded when displayed by git
rule update_repository:
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

# FIXME #1 Repository timestamp is not same as last commit date
rule update_repository_timestamps:
    message:
        "step: sets timestamp of repository files to last commit"
    shell:
        """
        {PACKAGE_PATH}/scripts/git_update_mtime.sh {config.parla_clarin.repository_folder}
        """

# FIXME #2 Handle case when files are removed from repository
rule sync_deleted_files:
    run:
        utility.sync_delta_names(
            config.parla_clarin.source_folder, "xml", config.extract_speeches.folder, "txt", delete=True
        )
