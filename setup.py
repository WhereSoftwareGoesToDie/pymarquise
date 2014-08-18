from setuptools import setup

import marquise.marquise
extension = marquise.marquise.FFI.verifier.get_extension()

with open('VERSION', 'r') as f:
    VERSION = f.readline().strip()


# These notes suggest that there's not yet any "correct" way to do packageable
# CFFI interfaces. For now I'm splitting the CFFI stuff from the python
# interface stuff, and it seems to do the job okay, though dealing with
# packages and modules is a flailfest at best for me.
# https://bitbucket.org/cffi/cffi/issue/109/enable-sane-packaging-for-cffi

setup(
    name="marquise",
    version=VERSION,
    description="Python bindings for libmarquise",
    author="Barney Desmond",
    author_email="engineering@anchor.net.au",
    maintainer="Anchor Engineering",
    maintainer_email="engineering@anchor.net.au",
    url="https://github.com/anchor/pymarquise",
    zip_safe=False,
    packages=[
        "marquise",
    ],
    package_data={"marquise" : ["marquise.h"]},
    ext_modules = [extension],
    include_package_data=True
)
