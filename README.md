# HiGlass Python

[![HiGlass](https://img.shields.io/badge/higlass-👍-red.svg?colorB=45afe5)](http://higlass.io)
[![Python](https://img.shields.io/pypi/v/higlass-python?colorB=6680ff)](https://pypi.org/project/higlass-python/)
[![Docs](https://img.shields.io/badge/docs-🎉-red.svg?colorB=af80ff)](https://docs.higlass.io/jupyter.html)
[![Build Status](https://travis-ci.org/higlass/higlass-python.svg?branch=master)](https://travis-ci.org/higlass/higlass-python)

Python bindings to the HiGlass for tile serving, view config generation, and Jupyter Notebook + Lab integration.

This package provide access to:
- server: a lightweight flask server
- tilesets: tileset API
- client: an API for generating view configs
- viewer: an API for launching HiGlass in Jupyter Notebook or Lab

## Installation

#### Requirements

- Python >= 3.7
- [FUSE](https://github.com/libfuse/libfuse) or [MacFuse](https://osxfuse.github.io/)
- Jupyter Notebook >= 5.7
- Jupyter Lab >= 0.35

#### Install package

First install `higlass-python` via pip:

```bash
pip install higlass-python
```

## Getting started

Take a look at [notebooks/Examples.ipynb](notebooks/Examples.ipynb) on how to get started.

## Documentation

There is more detailed documentation at [docs-python.higlass.io](https://docs.python.higlass.io).

## Development

* Install the package in _editable_ mode. (The module will be imported from the development directory, rather than copied to `site-packages`).

   ```bash
   pip install -e .
   ```

### Editing the docs

To work on the docs, start the autoserver and edit the rst files in the `docs` directory:

```bash
cd docs
./serve.sh
```

## Troubleshooting

- If you are running JupyterLab `v1.x` and ipywidgets `v7.5` and the HiGlass widget is not being displayed! Then you might have an incompatible widget installed that makes all other widgets fail. Try to deinstall all other widgets to test HiGlass separately before submitting a ticket. For more information see https://github.com/jupyter-widgets/ipywidgets/issues/2483#issuecomment-508643088
