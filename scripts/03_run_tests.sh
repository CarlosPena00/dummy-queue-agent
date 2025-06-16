#!/bin/bash
# Run tests with pytest and coverage
# Optional arguments can be passed to pytest

# Clean previous coverage data
coverage erase

# Run all tests by default with coverage
if [ $# -eq 0 ]; then
    coverage run -m pytest tests/
else
    # Pass all arguments to pytest
    coverage run -m pytest "$@"
fi

# Generate coverage report
coverage report -m
# Generate HTML report
coverage html
