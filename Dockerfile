FROM python:3.14-slim AS builder

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PYTHONDONTWRITEBYTECODE=1

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app
COPY pyproject.toml uv.lock README.md LICENSE /app/
COPY knowit/ /app/knowit/
RUN uv build --wheel


FROM python:3.14-slim

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

RUN pip install /usr/src/dist/knowit-*.whl

WORKDIR /

ENTRYPOINT ["knowit"]
CMD ["--help"]
