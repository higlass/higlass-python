.PHONY: build install clean all

install:
	python setup.py jsdeps
	jupyter nbextension install --py --symlink --sys-prefix higlass
	jupyter nbextension enable --py --sys-prefix higlass

uninstall:
	jupyter nbextension uninstall --py --sys-prefix higlass
	rm -rf higlass/static/
	rm -rf build

build:
	python setup.py jsdeps

clean:
	rm -rf higlass/static/
	rm -rf build
