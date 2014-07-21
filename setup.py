from setuptools import setup

import marquise.marquise
extension = marquise.marquise.ffi.verifier.get_extension()


# How to package??
# https://bitbucket.org/cffi/cffi/issue/109/enable-sane-packaging-for-cffi

with open('VERSION', 'r') as f:
	VERSION = f.readline().strip()


setup(
    name="marquise",
    version=VERSION,
    description="Python bindings for libmarquise",
    author="Sharif Olorin",
    author_email="sio@tesser.org",
    url="https://github.com/anchor/pymarquise",
    zip_safe=False,
    packages=[
        "marquise",
    ],
    ext_modules = [extension],
)
