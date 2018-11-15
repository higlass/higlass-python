from __future__ import print_function
from setuptools import setup, find_packages, Command
from setuptools.command.sdist import sdist
from setuptools.command.build_py import build_py
from setuptools.command.egg_info import egg_info
from subprocess import check_call
import os
import sys
import platform

here = os.path.dirname(os.path.abspath(__file__))
is_repo = os.path.exists(os.path.join(here, '.git'))

from distutils import log
log.set_verbosity(log.DEBUG)
log.info('setup.py entered')
log.info('$PATH=%s' % os.environ['PATH'])

LONG_DESCRIPTION = 'Python bindings for the HiGlass viewer'

version_ns = {}
with open(os.path.join(here, 'higlass_python', '_version.py')) as f:
    exec(f.read(), {}, version_ns)

setup_args = {
    'name': 'higlass_python',
    'version': version_ns['__version__'],
    'description': 'Python bindings for the HiGlass viewer',
    'long_description': LONG_DESCRIPTION,
    'include_package_data': True,
    'install_requires': [
        'clodius'
    ],
    'setup_requires': [
    ],
    'packages': find_packages(),
    'zip_safe': False,
    'author': 'Peter Kerpedjiev',
    'author_email': 'pkerpedjiev@gmail.com',
    'url': 'https://github.com/higlass/higlass-python',
    'keywords': [
        'higlass',
    ],
    'classifiers': [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Multimedia :: Graphics',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
}

setup(**setup_args)
