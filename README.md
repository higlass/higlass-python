# higlass-schema

[![PyPI](https://img.shields.io/pypi/v/higlass-schema.svg?color=green)](https://pypi.org/project/higlass-schema)
[![License](https://img.shields.io/pypi/l/gosling.svg?color=green)](https://github.com/higlass/higlass-schema/raw/main/LICENSE)

Pydantic models for HiGlass

```bash
pip install higlass-schema
```

🚧 👷


## Development

```bash
$ pip install -e .
$ higlass-schema check ./example.json # [--verbose]
$ higlass-schema export # prints JSON schema to stdout
```

## Release

```bash
git tag -a v0.0.0 -m "v0.0.0"
git push --follow-tags
```
