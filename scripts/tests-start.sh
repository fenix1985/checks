#!/bin/bash
set -e
set -x
#bash ./scripts/test.sh "$@"

#pytest --cov=app --cov-report=term-missing /app/tests "${@}"
pytest /app/tests "${@}"
