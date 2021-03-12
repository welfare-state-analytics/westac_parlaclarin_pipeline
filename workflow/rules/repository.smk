PARLA_CLARIN_CONFIG = config["parla_clarin"]

repository_folder = PARLA_CLARIN_CONFIG["repository_folder"]
root_folder = os.path.join(repository_folder, '..')


rule init_repository:
    message:
        "step: create shallow copy of ParlaClarin repository"
    output:
        directory(repository_folder),
    log:
        "init_repository.log",
    shell:
        f"""
           pushd . \
        && cd {root_folder} \
        && git clone --depth 1 {PARLA_CLARIN_CONFIG["repository_url"]} \
        && popd
        """


rule update_repository:
    message:
        "step: do a shallow update of ParlaClarin repository"
    shell:
        f"""\
           pushd . \
        && cd {config["parla_clarin"]["repository_folder"]} \
        && git fetch --depth 1 \
        && git reset --hard origin \
        && git clean -dfx \
        && popd \
        """


rule sync_deleted_files:
    run:
        utility.sync_delta_names(
            config['parla_clarin']['source_folder'], "xml", config['target_export_folder'], "txt", delete=True
        )
