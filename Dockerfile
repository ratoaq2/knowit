FROM python:3.14-slim AS builder

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PYTHONDONTWRITEBYTECODE=1

COPY --from=ghcr.io/astral-sh/uv:0.12.17 /uv /uvx /bin/

WORKDIR /app
COPY pyproject.toml uv.lock README.md LICENSE /app/
COPY knowit/ /app/knowit/
RUN uv build --wheel


FROM python:3.14-slim

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

RUN apt-get update \
 && apt-get install -y --no-install-recommends mediainfo=25.04* ffmpeg=7:7.1.5* mkvtoolnix=92.0* \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/dist /usr/src/dist

RUN pip install --no-cache-dir "$(ls /usr/src/dist/knowit-*.whl)[pint]"

WORKDIR /

ENTRYPOINT ["knowit"]
CMD ["--help"]
