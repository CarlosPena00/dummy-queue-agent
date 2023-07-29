# My Python Template

```sh
mamba env create
conda activate template_python
pip-sync requirements-dev.txt
pre-commit install

# After update `setup.cfg`
pip-compile setup.cfg --resolver backtracking -o requirements.txt
pip-compile setup.cfg --resolver backtracking -o requirements-dev.txt --extra dev
```

## Run
```sh
# start docker:
sh scripts/00_start.sh
```
