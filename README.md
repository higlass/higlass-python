# higlass-python #

Python bindings to the HiGlass viewer.

### For development ###

* Install the package in _editable_ mode. (The module will be imported from the development directory, rather than copied to `site-packages`).

```bash
$ pip install -e .
```

* Build and enable the Jupyter Notebook Extension. (With the `--symlink` option, the assets in `higlass/static` are linked to the extension registry rather than copied.)

```bash
$ python setup.py jsdeps
$ jupyter nbextension enable --py --sys-prefix widgetsnbextension
$ jupyter nbextension install --py --symlink --sys-prefix higlass
$ jupyter nbextension enable --py --sys-prefix higlass
```

* Uninstall the Jupyter Notebook Extension

```bash
$ jupyter nbextension uninstall --py --sys-prefix higlass
```

* Experimental: install the Jupyter Lab Extension

```bash
$ cd js && jupyter labextension link .
```
