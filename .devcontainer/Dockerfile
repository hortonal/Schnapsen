FROM continuumio/miniconda3
COPY requirements-dev.txt .
COPY requirements.txt .
RUN conda create -n default_env python=3.12
RUN echo "source activate default_env" > ~/.bashrc
ENV PATH /opt/conda/envs/default_env/bin:$PATH
RUN pip install -r requirements.txt
RUN pip install -r requirements-dev.txt
# RUN pip install -e .
