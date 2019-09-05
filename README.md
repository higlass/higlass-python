# HiGlass Python

[![HiGlass](https://img.shields.io/badge/higlass-👍-red.svg?colorB=45afe5)](http://higlass.io)
[![Docs](https://img.shields.io/badge/docs-🎉-red.svg?colorB=6680ff)](https://higlass.io/docs/python_api.html)
[![Python](https://img.shields.io/badge/python-😍-red.svg?colorB=af80ff)](https://higlass.io/docs/python_api.html)
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
- Jupyter Lab >= 0.35 & < 1.0
- ipywidgets <= 7.4.2

#### Install package

First install `higlass-python` via pip:

```bash
pip install higlass-python
```

#### Jupyter Notebook integration

Open a terminal and execute the following code to activate the integration:

```bash
# The following is only required if you have not enabled the ipywidgets nbextension yet
jupyter nbextension enable --py --sys-prefix widgetsnbextension
jupyter nbextension install --py --sys-prefix higlass
jupyter nbextension enable --py --sys-prefix higlass
```

#### Jupyter Lab integration

Open a terminal and execute the following code to activate the integration:

```bash
# The following is only required if you have not enabled the jupyterlab manager yet
jupyter labextension install @jupyter-widgets/jupyterlab-manager
jupyter labextension install higlass-jupyter
```

## Getting started

Take a look at [notebooks/Examples.ipynb](notebooks/Examples.ipynb) on how to get started.

## Development

* Install the package in _editable_ mode. (The module will be imported from the development directory, rather than copied to `site-packages`).

   ```bash
   pip install -e .
   ```

* Build and enable the Jupyter Notebook Extension. (With the `--symlink` option, the assets in `higlass/static` are linked to the extension registry rather than copied.)

   ```bash
   python setup.py jsdeps
   jupyter nbextension enable --py --sys-prefix widgetsnbextension
   jupyter nbextension install --py --symlink --sys-prefix higlass
   jupyter nbextension enable --py --sys-prefix higlass
   ```

* Uninstall the Jupyter Notebook Extension

   ```bash
   jupyter nbextension uninstall --py --sys-prefix higlass
   ```

* Experimental: install the Jupyter Lab Extension

   ```bash
   cd js && jupyter labextension link .
   ```

## Trouble Shooting

- If you are running JupyterLab `v1.x` and ipywidgets `v7.5` and the HiGlass widget is not being displayed! Then you might have an incompatible widget installed that makes all other widgets fail. Try to deinstall all other widgets to test HiGlass separately before submitting a ticket. For more information see https://github.com/jupyter-widgets/ipywidgets/issues/2483#issuecomment-508643088
