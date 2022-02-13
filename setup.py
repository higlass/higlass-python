from setuptools import setup, find_packages
import os
import io
import re
from distutils import log


log.set_verbosity(log.DEBUG)
log.info("setup.py entered")
log.info("$PATH=%s" % os.environ["PATH"])

HERE = os.path.dirname(os.path.abspath(__file__))

def read(*parts, **kwargs):
    filepath = os.path.join(HERE, *parts)
    encoding = kwargs.pop("encoding", "utf-8")
    with io.open(filepath, encoding=encoding) as fh:
        text = fh.read()
    return text


def get_version():
    version = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
        read("higlass", "_version.py"),
        re.MULTILINE,
    ).group(1)
    return version


def get_requirements(path):
    content = read(path)
    return [req for req in content.split("\n") if req != "" and not req.startswith("#")]


setup_args = {
    "name": "higlass-python",
    "version": get_version(),
    "packages": find_packages(),
    "license": "MIT",
    "description": "Python bindings for the HiGlass viewer",
    "long_description": read("README.md"),
    "long_description_content_type": "text/markdown",
    "url": "https://github.com/higlass/higlass-python",
    "include_package_data": True,
    "zip_safe": False,
    "author": "Peter Kerpedjiev",
    "author_email": "pkerpedjiev@gmail.com",
    "keywords": ["higlass"],
    "classifiers": [
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Multimedia :: Graphics",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    "install_requires": get_requirements("requirements.txt"),
    "setup_requires": [],
    "tests_require": ["pytest"],
}

setup(**setup_args)
