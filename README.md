# HiGlass Python

[![HiGlass](https://img.shields.io/badge/higlass-👍-red.svg?colorB=45afe5)](http://higlass.io)
[![Docs](https://img.shields.io/badge/docs-🎉-red.svg?colorB=6680ff)](https://higlass.io/docs/python_api.html)
[![Python](https://img.shields.io/badge/python-😍-red.svg?colorB=af80ff)](https://higlass.io/docs/python_api.html)

Python bindings to the HiGlass viewer.

### Requirements

- Python >= 3.6
- Jupyter Notebook >= 5.7
- Jupyter Lab >= 0.35

### Installation

First install `higlass-python` via pip:

```bash
pip install higlass-python
```

If you're using **Jupyter Notebook**, open a terminal and execute the following code to activate the integrations:

```bash
# Only required if you have not enabled the ipywidgets nbextension yet
jupyter nbextension enable --py --sys-prefix widgetsnbextension

# For notebook
jupyter nbextension enable --py --sys-prefix higlass

```

If you're using **Jupyter Lab**, open a terminal and execute the following code to activate the integrations:

```bash
# Only required if you have not enabled the jupyterlab manager yet
jupyter labextension install @jupyter-widgets/jupyterlab-manager

# For lab
jupyter labextension install higlass
```

### Getting started

Take a look at [notebooks/Examples.ipynb](notebooks/Examples.ipynb) on how to get started.

### Development

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
