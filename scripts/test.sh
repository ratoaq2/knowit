#!/bin/bash

set -ex

uv run ruff check .
uv run ruff format --check .
uv run mypy knowit tests
uv run pytest --cov-report term --cov-report html --cov knowit -vv tests
