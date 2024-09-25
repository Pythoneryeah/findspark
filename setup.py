#!/usr/bin/env python

import sys

from distutils.core import setup

if any(arg.startswith('bdist') for arg in sys.argv):
    import setuptools

version_ns = {}
with open('findspark_msxf.py') as f:
    for line in f:
        if line.startswith('__version__'):
            exec(line, version_ns)
            break
    
setup(
    name='findspark_msxf',
    version=version_ns['__version__'],
    py_modules=['findspark_msxf, condaUtils'],
    description="Find pyspark to make it importable.",
    long_description="""
        Provides findspark_msxf.init() to make pyspark importable as a regular library.
    """,
    license="BSD (3-clause)",
    author="Min RK",
    author_email="benjaminrk@gmail.com",
    url="https://github.com/minrk/findspark",
)