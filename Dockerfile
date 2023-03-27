FROM nvidia/cuda:11.6.2-base-ubuntu20.04

LABEL MAINTAINER Roger Mähler <roger dot mahler at umu dot se>

ENV SHELL=/bin/bash
ENV DEBIAN_FRONTEND=noninteractive

USER root

RUN apt update \
    && apt upgrade -y
RUN apt install -y git \
        build-essential libssl-dev zlib1g-dev \
        libbz2-dev libreadline-dev libsqlite3-dev curl \
        libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*
    # apt clean && \
    # rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ARG APP_UID="201"
ARG APP_GID="2001"
ARG APP_USER="pyriksprot"

RUN addgroup --gid $APP_GID "${APP_USER}"
RUN adduser ${APP_USER} --uid ${APP_UID} --gid ${APP_GID} --disabled-password --gecos '' --shell /bin/bash


#  && adduser -a -G sudo ${APP_USER} \
#  && echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

USER $APP_USER

ENV HOME=/home/$APP_USER

WORKDIR ${HOME}

ARG PYTHON_VERSION="3.11"
ENV PYENV_ROOT ${HOME}/.pyenv
ENV PATH $PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH

RUN curl https://pyenv.run | bash
RUN pyenv update \
    && pyenv install ${PYTHON_VERSION} \
    && pyenv global ${PYTHON_VERSION}

WORKDIR ${HOME}/work

ARG PACKAGE_VERSION=2023.3.1
RUN python -m venv .venv \
  && . .venv/bin/activate \
  && python -m pip install pip --upgrade \
  && pip install pyriksprot-tagger:APP_VERSION

ENV PATH="${HOME}/work/.venv/bin:/usr/local/bin:$PATH"

RUN pip

# sudo apt update && sudo apt upgrade -y
# # Run the container with the current and home directories mounted.
# docker run -it --rm --network host \
#     --mount "type=bind,src=$(pwd),dst=/repo" \
#     --mount "type=bind,src=$HOME,dst=$homedst" \
#     --mount "type=bind,src=/etc/passwd,dst=/etc/passwd" \
#     "${passopt[@]}" "$SQITCH_IMAGE" "$@"

# # docker run --rm --runtime=nvidia --gpus all nvidia/cuda:11.6.2-base-ubuntu20.04 nvidia-smi
# # +---------------------------------------------------------------------------------------+
# # | NVIDIA-SMI 530.30.02              Driver Version: 530.30.02    CUDA Version: 12.1     |
# # |-----------------------------------------+----------------------+----------------------+
# # | GPU  Name                  Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
# # | Fan  Temp  Perf            Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
# # |                                         |                      |               MIG M. |
# # |=========================================+======================+======================|
# # |   0  NVIDIA GeForce RTX 4090         Off| 00000000:08:00.0 Off |                  Off |
# # |  0%   48C    P8               32W / 450W|   4709MiB / 24564MiB |      0%      Default |
# # |                                         |                      |                  N/A |
# # +-----------------------------------------+----------------------+----------------------+

# # +---------------------------------------------------------------------------------------+
# # | Processes:                                                                            |
# # |  GPU   GI   CI        PID   Type   Process name                            GPU Memory |
# # |        ID   ID                                                             Usage      |
# # |=======================================================================================|
# # +---------------------------------------------------------------------------------------+
