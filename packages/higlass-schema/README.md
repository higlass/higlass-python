# higlass-schema

[![PyPI](https://img.shields.io/pypi/v/higlass-schema.svg?color=green)](https://pypi.org/project/higlass-schema)
[![License](https://img.shields.io/pypi/l/gosling.svg?color=green)](https://github.com/higlass/higlass-schema/raw/main/LICENSE)

Pydantic models for HiGlass

```bash
pip install higlass-schema
```

## Development

Try it out:

```bash
$ uv run higlass-schema check ./example.json # [--verbose]
$ uv run higlass-schema export # prints JSON schema to stdout
```

Testing, linting, & formatting are enforced in CI. Locally, you can run:

```sh
uv run pytest # tests
uv run ruff check # linting
uv run ruff format --check # formatting (remove --check to apply)
```
