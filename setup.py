#! /usr/bin/env python

from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize

extensions = [
    Extension(
        "_marquise", 
        ["marquise/_marquise.pyx"],
        include_dirs=["marquise"],
        libraries=["marquise"],
    ),
]

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
    ext_modules = cythonize(extensions),
)
