FROM python:3.11-slim as builder

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.3.1 \
    POETRY_VIRTUALENVS_CREATE=0

RUN pip install "poetry==$POETRY_VERSION"

WORKDIR /app
COPY poetry.lock pyproject.toml /app/
RUN poetry install --no-interaction --no-ansi --only main
COPY README.md /app/
COPY knowit/ /app/knowit/
RUN poetry build --no-interaction --no-ansi


FROM python:3.11-slim

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

RUN apt-get update \
 && apt-get install -y --no-install-recommends mediainfo ffmpeg mkvtoolnix \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/dist /usr/src/dist

RUN pip install /usr/src/dist/knowit-*.tar.gz

WORKDIR /

ENTRYPOINT ["knowit"]
CMD ["--help"]
