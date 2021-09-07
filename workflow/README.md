# Parla-Clarin to penelope pipeline

## How to install

## How to configure

## How to setup data

### Riksdagens corpus

Create a shallow clone (no history) of repository:

```bash
make init-repository
```

Sync shallow clone with changes on origin (Github):

```bash
make update-repositoryupdate_repository_timestamps
```

Update modified date of repository file. This is necessary since the pipeline uses last commit date of
each XML-files to determine which files are outdated, whilst `git clone` sets current time.

```bash
$ make update-repository-timestamps
or
$ scripts/git_update_mtime.sh path-to-repository
```

## How to annotate speeches

```bash
make annotate
or
$ nohup poetry run snakemake -j4 --keep-going --keep-target-files &
```

Windows:

```bash
poetry shell
bash
nohup poetry run snakemake -j4 -j4 --keep-going --keep-target-files &
```

Run a specific year:

```bash
poetry shell
bash
nohup poetry run snakemake --config -j4 --keep-going --keep-target-files &
```
