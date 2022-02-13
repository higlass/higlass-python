.PHONY: install uninstall build clean publish

# Build and installation
install:
	pip install -v -e .
	pip install -r requirements-dev.txt

uninstall:
	pip uninstall higlass-python

build:
	python setup.py

clean:
	rm -rf build/
	rm -rf dist/

# Publishing tools
bump-patch:
	cd js && npm version patch
	echo "__version__ = \"`node -p "require('./js/package.json').version"`\"" > higlass/_version.py
	git add ./js/package.json ./higlass/_version.py
	git commit -m "Bump to v`node -p "require('./js/package.json').version"`"

bump-minor:
	cd js && npm version minor
	echo "__version__ = \"`node -p "require('./js/package.json').version"`\"" > higlass/_version.py
	git add ./js/package.json ./higlass/_version.py
	git commit -m "Bump to v`node -p "require('./js/package.json').version"`"

bump-major:
	cd js && npm version major
	echo "__version__ = \"`node -p "require('./js/package.json').version"`\"" > higlass/_version.py
	git add ./js/package.json ./higlass/_version.py
	git commit -m "Bump to v`node -p "require('./js/package.json').version"`"

publish:
	git tag -a "v`node -p "require('./js/package.json').version"`" -m "Version `node -p "require('./js/package.json').version"`"
	git push --follow-tags
