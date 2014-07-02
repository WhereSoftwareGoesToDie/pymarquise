from distutils.core import setup

import marquise
print(marquise.ffi.verifier.get_extension())


# How to package??
# https://bitbucket.org/cffi/cffi/issue/109/enable-sane-packaging-for-cffi

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
    ext_modules = [marquise.ffi.verifier.get_extension()],
)
