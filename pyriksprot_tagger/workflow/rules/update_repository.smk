# type: ignore
# pylint: skip-file, disable-all
from os.path import basename

cfg = cfg

repository_name: str = basename(cfg.get("corpus.repository.folder"))

rule init_repository:
    log:
        cfg.get("log_filename"),
    message:
        "step: create shallow copy of ParlaClarin repository"
    output:
        directory(cfg.get("corpus.repository.folder")),
    log:
        "init_repository.log",
    shell:
        f"""
           pushd . \
        && cd {cfg.get("parent_folder")} \
        && git clone --branch {cfg.get("version")} --depth 1 {cfg.get("corpus.repository.url")} \
        && cd {repository_name} \
        && git config core.quotepath off \
        && popd
        """


rule update_repository:
    log:
        cfg.get("log_filename"),
    message:
        "step: do a shallow update of ParlaClarin repository"
    shell:
        f"""\
           pushd . \
        && cd {cfg.get("corpus.repository.folder")} \
        && git fetch --depth 1 \
        && git reset --hard origin \
        && git clean -dfx \
        && git config core.quotepath off \
        && popd \
        """

rule update_repository_timestamps:
    # log:
    #     cfg.get("log_filename"),
    message:
        "step: sets timestamp of repository files to last commit"
    shell:
        """
        {PACKAGE_PATH}/scripts/update-timestamps {cfg.get("corpus.repository.folder")}
        """


rule sync_deleted_files:
    # log:
    #     cfg.get("log_filename"),
    run:
        utility.sync_delta_names(cfg.("corpus.folder"), "xml", cfg.get("tagged_frames.folder"), "zip", delete=True)
        # utility.sync_delta_names(
        #     cfg.get("corpus.folder"), "xml", cfg.get("extract.folder"), "txt", delete=True
        # )

