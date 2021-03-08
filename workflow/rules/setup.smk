# update_repository        : does a shallow update on Para-Clarin  repository

PARLA_CLARIN_CONFIG = config["parla_clarin"]


rule update_repository:
    shell:
        f"""\
           pushd . \
        && cd {config["parla_clarin"]["repository_folder"]} \
        && git fetch --depth 1 \
        && git reset --hard origin \
        && git clean -dfx \
        && popd \
        """


# init_repository          : initializes shallow clone of Para-Clarin repository
rule init_repository:
    output:
        directory(PARLA_CLARIN_CONFIG["repository_folder"]),
    shell:
        f"""
        git clone --depth 1 {PARLA_CLARIN_CONFIG["repository_url"]}
        """
