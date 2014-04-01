#! /usr/bin/env python

from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

setup(
    name="marquise",
    version="1.2.2",
    description="Python bindings for libmarquise",
    author="Sharif Olorin",
    author_email="sio@tesser.org",
    url="https://github.com/anchor/pymarquise",
    packages=[
        "marquise",
    ],
    requires=[
        "pyzmq",
    ],
)
