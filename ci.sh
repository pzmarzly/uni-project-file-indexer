#!/bin/bash
set -eu
set -x

poetry run coverage run -m unittest discover -s tests
poetry run coverage report
poetry run mypy -p indexme --namespace-packages
poetry run pdoc --html . --force
