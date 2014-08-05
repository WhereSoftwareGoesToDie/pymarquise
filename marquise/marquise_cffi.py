# pylint: disable=line-too-long
# pylint: disable=bad-whitespace

"""This module holds all the CFFI stuff, so that the binding shim can be
handled separately from the interface code. The shim compiles to a .so library,
and the interface stays as a pure Python library, importing the shim.
"""

import os.path

from .oslo_strutils import safe_encode, safe_decode
import six

from cffi import FFI as FFI_CONSTRUCTOR
FFI = FFI_CONSTRUCTOR()

def cprint(ffi_string):
    """Return a UTF-8 Python string for an FFI bytestring."""
    return safe_decode(FFI.string(ffi_string), 'utf8')

def cstring(new_string):
    """Return a new FFI string for a provided UTF-8 Python string."""
    return FFI.new('char[]', safe_encode(new_string, 'utf8') )

def len_cstring(new_string):
    """Return the length in bytes for a UTF-8 Python string."""
    return len(safe_encode(new_string, 'utf8'))

def is_cnull(maybe_null):
    """Return True if `maybe_null` is a null pointer, otherwise return False."""
    return maybe_null == FFI.NULL


# This kinda beats dragging the header file in here manually, assuming you can
# clean it up suitably.  Assume that you've symlinked to marquise.h from here.
def get_libmarquise_header():
    """Read the libmarquise header to extract definitions."""
    # Header file is packaged in the same place as the rest of the
    # module.
    header_path = os.path.join(os.path.dirname(__file__), "marquise.h")
    with open(header_path) as header:
        libmarquise_header_lines = header.readlines()

    libmarquise_header_lines = [ line for line in libmarquise_header_lines if not line.startswith('#include ') and not line.startswith('#define ') ]
    libmarquise_header_lines = [ line for line in libmarquise_header_lines if not line.startswith('#include ') ]
    return ''.join(libmarquise_header_lines)


# Get all our cdefs from the headers.
FFI.cdef(get_libmarquise_header())


# Throw libmarquise at CFFI, let it do the hard work. This gives us
# API-level access instead of ABI access, and is generally preferred.
C_LIBMARQUISE = FFI.verify("""#include "marquise.h" """, include_dirs=['./'], libraries=['marquise'], modulename='marquise_cffi' )
