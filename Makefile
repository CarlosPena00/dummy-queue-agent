PROJECT_NAME := $(shell basename "$$(pwd)")

.PHONY: create activate deps update build run clean

create:
	mamba env create -n $(PROJECT_NAME) --file environment.yml

activate:
# TODO: return the activated environment to the user's terminal
	echo mamba activate $(PROJECT_NAME)

# Function to install development dependencies
deps:
	pip-sync requirements-dev.txt
	pre-commit install

# Function to just update requirements[-dev].txt (not install)
update:
	pip-compile setup.cfg --resolver backtracking -o requirements.txt -v
	pip-compile setup.cfg --resolver backtracking -o requirements-dev.txt --extra dev -v

build:
	docker build . -t $(PROJECT_NAME)

run:
	docker run -p 8000:8000 --rm -it $(PROJECT_NAME)

compose:
	docker compose up --build

# clean python/pip cache files
clean:
	find . -name "__pycache__" -exec rm -r {} +
	find . -name "*.pyc" -exec rm {} +
