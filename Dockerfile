# https://quay.io/repository/jupyter/base-notebook?tab=tags https://github.com/jupyter/docker-stacks/blob/main/images/base-notebook/Dockerfile
FROM quay.io/jupyter/base-notebook:lab-4.3.6 AS base_image

# https://github.com/moby/buildkit/blob/master/frontend/dockerfile/docs/reference.md#example-cache-apt-packages
USER root
RUN rm -f /etc/apt/apt.conf.d/docker-clean; echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
  --mount=type=cache,target=/var/lib/apt,sharing=locked \
  apt-get update && apt-get install -yq --no-install-recommends \
    # memray's native mode resolves symbols using debuginfod, https://bloomberg.github.io/memray/native_mode.html#debuginfod-integration
    debuginfod build-essential && \
  rm -rf $HOME/work
ENV DEBUGINFOD_URLS="https://debuginfod.ubuntu.com/"




# $NB_USER is jovyan
USER $NB_USER


# Execute all following RUN commands inside the conda "base" environment, https://pythonspeed.com/articles/activate-conda-dockerfile
SHELL ["conda", "run", "--no-capture-output", "-n", "base", "/bin/bash", "-c"]

# Try a fast pip alternative
RUN pip install uv==0.6.6

## Add python packages, https://stackoverflow.com/questions/58018300/using-a-pip-cache-directory-in-docker-builds
## Create cache directory to avoid root ownership
RUN mkdir -p $HOME/.cache
RUN --mount=type=cache,uid=$NB_UID,mode=7777,target=$HOME/.cache/uv \
  uv pip install \
    scipy==1.16.1 \
    # try to automatically import missing imports \
    # jupyterlab-pyflyby==5.1.2 \
    # pyflyby==1.9.11 \
    # visualization
    matplotlib==3.10.1 \
    # just-in-time compiler for numerical functions
    numba==0.61.2 \
    # arrays, version set by numba
    numpy==2.2.0 # && py pyflyby.install_in_ipython_config_file

