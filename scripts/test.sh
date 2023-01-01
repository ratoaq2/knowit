#!/bin/bash

set -ex

flake8 knowit
mypy knowit
pytest --cov-report term --cov-report html --cov knowit -vv tests