# -*- coding: utf-8 -*-

import os
import re

from setuptools import setup


def read(filename):
    with open(os.path.join(os.path.dirname(__file__), filename)) as fp:
        return fp.read()


def find_version(path):
    version_file = read(path)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name='ebird-pages',
    version=find_version("ebird/pages/__init__.py"),
    description='Scrapers for pages on the eBird web site',
    long_description=read("README.md"),
    author='ProjectBabbler',
    author_email='projectbabbler@gmail.com',
    url='http://pypi.python.org/pypi/ebird-pages/',
    license='GPL',
    keywords='eBird web scraper',
    packages=['ebird.pages'],
    test_suite='tests.unit',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Natural Language :: English',
        'Topic :: Utilities',
        'Topic :: Internet',
    ],
    install_requires=[
        'beautifulsoup4',
        'lxml',
        'requests',
    ],
)
