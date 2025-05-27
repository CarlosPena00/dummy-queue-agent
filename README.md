# My Python Template

```sh
make

# After update `setup.cfg`
make lockdeps
make deps
```

## Run
```sh
# start docker:
sh scripts/00_start.sh
```


## Add Secrets

Secrets and configmaps should be declared with their respective types in the src.core.settings file.

In the case of secrets, we must only place their values ​​in the .env file (non-versioned file).

```py
python -m src.core.settings
> API_KEY='FOO'
```

> echo 'API_KEY=123' >> .env

```py
python -m src.core.settings
> API_KEY='123'
```
