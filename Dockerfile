FROM python:3.11-alpine as python-base
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.4  \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="." \
    VENV_PATH=".venv"
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

FROM python-base as builder-base
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    curl \
    build-essential \
    libcurl4-openssl-dev \
    libssl-dev
RUN curl -sSL https://install.python-poetry.org | python3 -
WORKDIR $PYSETUP_PATH
COPY poetry.lock pyproject.toml ./
RUN poetry install --without dev

FROM python-base as production
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    curl
WORKDIR $PYSETUP_PATH
COPY src $PYSETUP_PATH/src
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]