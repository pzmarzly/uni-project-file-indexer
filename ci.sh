#!/bin/bash
set -eu
set -x

black --check indexme
autoflake --check --remove-unused-variables --remove-all-unused-imports -r indexme
isort --check indexme
poetry run mypy -p indexme --namespace-packages --strict

black --check tests
autoflake --check --remove-unused-variables --remove-all-unused-imports -r tests
isort --check tests
poetry run mypy -p tests --namespace-packages --strict

poetry run coverage run -m unittest discover -s tests
poetry run coverage report

poetry run pdoc --html . --force
