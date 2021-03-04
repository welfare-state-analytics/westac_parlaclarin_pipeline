# update_repository        : does a shallow update on Para-Clarin  repository
rule update_repository:
    shell:
        f"""\
           pushd . \
        && cd {config["repository_folder"]} \
        && git fetch --depth 1 \
        && git reset --hard origin \
        && git clean -dfx \
        && popd \
        """


# init_repository          : initializes shallow clone of Para-Clarin repository
rule init_repository:
    output:
        directory(config["repository_folder"]),
    shell:
        f'git clone --depth 1 {config["source_repository_url"]}'
