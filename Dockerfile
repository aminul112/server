
FROM python:3.9-slim as python-base

ENV PYTHONUNBUFFERED 1
ENV PIP_DISABLE_PIP_VERSION_CHECK on
ENV PIP_DEFAULT_TIMEOUT 100
ENV PIP_NO_CACHE_DIR off
ENV POETRY_VERSION 1.1.12
ENV POETRY_HOME /opt/poetry
ENV POETRY_VIRTUALENVS_IN_PROJECT true
ENV POETRY_NO_INTERACTION 1
ENV PYSETUP_PATH /opt/pysetup
ENV VENV_PATH /opt/pysetup/.venv

ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"


FROM python-base as builder-base

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    curl \
    build-essential

# install poetry
RUN pip install poetry==$POETRY_VERSION && \
    poetry --version

WORKDIR $PYSETUP_PATH
COPY pyproject.toml poetry.lock ./

RUN poetry install


FROM python-base as production

COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH

COPY main.py /main.py
COPY messages_pb2.py /messages_pb2.py
#CMD ["python", "./main.py"]
