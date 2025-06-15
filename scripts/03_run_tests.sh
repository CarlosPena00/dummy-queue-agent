#!/bin/bash
# Run tests with pytest
# Optional arguments can be passed to pytest

# Run all tests by default
if [ $# -eq 0 ]; then
    python -m pytest tests/
else
    # Pass all arguments to pytest
    python -m pytest "$@"
fi
