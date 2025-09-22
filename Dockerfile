FROM c2dhunilu/journal-of-digital-history-jupyter
#FROM jupyter/base-notebook:python-3.9.5
USER root
RUN apt-get update && apt-get install -y git

USER jovyan
WORKDIR $HOME
## Install Python citation manager
RUN pip install --no-cache-dir jupyterlab-citation-manager
COPY requirements.txt .
RUN pip install -r requirements.txt
ENTRYPOINT jupyter lab --allow-root