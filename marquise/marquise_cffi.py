# Put all the CFFI stuff into a separate module so that the binding itself can
# be distributed separately from the CFFI stuff, which compiles to a .so
# library.

from cffi import FFI
ffi = FFI()

# XXX: This is a lazy hack alternative to fetching the real definition of
# EINVAL.
EINVAL = 2

def cprint(ffi_string):
	"""Return a UTF-8 Python string for an FFI bytestring."""
	return str(ffi.string(ffi_string), 'utf8')

def cstring(new_string):
	"""Return a new FFI string for a provided UTF-8 Python string."""
	return ffi.new('char[]', bytes(new_string, 'utf8') )

def len_cstring(new_string):
	"""Return the length in bytes for a UTF-8 Python string."""
	return len(bytes(new_string, 'utf8'))

def is_cnull(maybe_null):
	"""Return True if `maybe_null` is a null pointer, otherwise return False."""
	return maybe_null == ffi.NULL


# This kinda beats dragging the header file in here manually, assuming you can
# clean it up suitably.  Assume that you've symlinked to marquise.h from here.
def get_libmarquise_header():
	"""Read the canonical marquise headers to extract definitions."""
	with open('marquise.h') as f:
		libmarquise_header_lines = f.readlines()

	libmarquise_header_lines = [ line for line in libmarquise_header_lines if not line.startswith('#include ') and not line.startswith('#define ') ]
	libmarquise_header_lines = [ line for line in libmarquise_header_lines if not line.startswith('#include ') ]
	return ''.join(libmarquise_header_lines)


# Get all our cdefs from the headers.
ffi.cdef(get_libmarquise_header())


# Throw libmarquise at CFFI, let it do the hard work. This gives us
# API-level access instead of ABI access, and is generally preferred.
c_libmarquise = ffi.verify("""#include "marquise.h" """, include_dirs=['./'], libraries=['marquise'], modulename='marquise_cffi' )
