.PHONY: build install uninstall clean nbext-deps install-nbext uninstall-nbext labext-deps install-labext uninstall-labext

install:
	pip install -e .

uninstall:
	pip uninstall higlass-python

build:
	python setup.py jsdeps

clean:
	rm -rf higlass/static/
	rm -rf build

clean-npm:
	rm -rf js/dist
	rm -rf js/node_modules

nbext-deps:
	pip install jupyter_contrib_nbextensions
	jupyter contrib nbextension install --sys-prefix
	jupyter nbextension enable --py --sys-prefix widgetsnbextension

install-nbext:
	jupyter nbextension install --py --symlink --sys-prefix higlass
	jupyter nbextension enable --py --sys-prefix higlass

uninstall-nbext:
	jupyter nbextension uninstall --py --sys-prefix higlass


labext-deps:
	jupyter labextension install @jupyter-widgets/jupyterlab-manager

install-labext:
	cd js && jupyter labextension link .

uninstall-labext:
	cd js && jupyter labextension unlink .
