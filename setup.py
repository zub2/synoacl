#!/usr/bin/env python
from setuptools import setup, find_packages

from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, "DESCRIPTION.rst"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name = "synoacl",
    version = "0.0.1",
    description = "A simple wrapper around Synology\"s synoacltool.",
    long_description = long_description,
    url = "https://github.com/zub2/synoacl",
    author = "David Kozub",
    author_email = "zub.272@gmail.com",
    license = "GPLv3+",
    classifiers = [
        "Development Status :: 3 - Alpha",

        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Filesystems",

        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",

        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
    ],
    keywords = "synology acl nas",
    packages = find_packages(exclude = ["docs", "tests"]),
    test_suite = "tests",
)
