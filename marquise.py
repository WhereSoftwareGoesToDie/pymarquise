import os
from cffi import FFI

ffi = FFI()


LIBMARQUISE_SRC_PATH = '/home/barney/git/libmarquise/src'
def marquise_file(filename=''):
	return os.path.join(LIBMARQUISE_SRC_PATH, filename)


# This kinda beats dragging the header file in here manually, assuming you can
# clean it up suitably.
def get_libmarquise_header():
	with open(marquise_file('marquise.h')) as f:
		libmarquise_header_lines = f.readlines()

	libmarquise_header_lines = [ line for line in libmarquise_header_lines if not line.startswith('#include ') and not line.startswith('#define ') ]
	libmarquise_header_lines = [ line for line in libmarquise_header_lines if not line.startswith('#include ') ]
	return ''.join(libmarquise_header_lines)

# Get all our cdefs from the headers
ffi.cdef(get_libmarquise_header())


def cprint(ffi_string):
	# ffi.string() returns bytes()
	return str(ffi.string(ffi_string), 'utf8')

def cstring(new_string):
	# Assume UTF8 input
	return ffi.new('char[]', bytes(new_string, 'utf8') )

def is_cnull(maybe_null):
	return maybe_null == ffi.NULL

EINVAL = 2




# Throw libmarquise at CFFI, let it do the hard work. This gives us
# API-level access instead of ABI access, and is generally preferred.
c_libmarquise = ffi.verify("""#include "marquise.h" """, include_dirs=[marquise_file()], libraries=['marquise'] )


# This shouldn't be needed any more, I don't think CFFI needs to see the C.
# https://gist.github.com/barneydesmond/8c194e891d96d9cfef9a
# https://groups.google.com/forum/#!msg/python-cffi/jI7YUafYlwc/FMyGz69rLf8J
#ffi.verify(open(marquise_file('marquise.c'), 'r').read(), include_dirs=[marquise_file()], libraries=['marquise'] )
#ffi.verify(sources=[marquise_file('marquise.c')], include_dirs=[marquise_file()], libraries=['marquise'] )
#ffi.verify("""#include "marquise.h" """, sources=[marquise_file('marquise.c')], include_dirs=[marquise_file()], libraries=['marquise'] )


class Marquise(object):
	#typedef struct {
	#        char *spool_path;
	#        FILE *spool;
	#} marquise_ctx;

	def __init__(self, namespace):
		self.namespace_c = cstring(namespace)
		self.marquise_ctx = c_libmarquise.marquise_init(self.namespace_c)
		if is_cnull(self.marquise_ctx):
			if ffi.errno == EINVAL:
				raise ValueError("Invalid namespace: {}".format(namespace))
			raise RuntimeError("Something went wrong, got NULL instead of a marquise_ctx. build_spool_path() failed, or malloc failed. errno is {}".format(ffi.errno))

		self.spool_path = cprint(self.marquise_ctx.spool_path)

	def __str__(self):
		return "<Marquise handle spooling to {}>".format(self.spool_path)

	def send_simple(self, datapoint):
		"""
		Queue a simple datapoint (i.e., a 64-bit word) to be sent by 
		the Marquise daemon. Returns zero on success and nonzero on 
		failure.

		int marquise_send_simple(marquise_ctx *ctx, uint64_t address, uint64_t timestamp, uint64_t value);
		"""
		# will need to call ffi.new and stuff around here to make up the C datatypes and dispatch them.
		address = 123456
		timestamp = 18
		retval = c_libmarquise.marquise_send_simple(self.marquise_ctx, address, timestamp, datapoint)
		print(retval)
		if retval == 0:
			return True
		return False

	def send_extended(self, datapoint):
		"""
		Queue an extended datapoint (i.e., a string) to be sent by the 
		Marquise daemon. Returns zero on success and nonzero on failure.

		int marquise_send_extended(marquise_ctx *ctx, uint64_t address, uint64_t timestamp, char *value, size_t value_len);
		"""
		pass
		# will need to call ffi.new and stuff around here to make up the C datatypes and dispatch them.



# print("---- Hack a marquise_ctx* out of thin air")
# ctx = ffi.new("marquise_ctx*")
# ctx.spool_path = cstring("/vur/lob/foo")
# print("The spool path is:")
# print( cprint(ctx.spool_path) )


# XXX: Not sure this is going to work, I need some test vectors to make sure
# I'm seeing output that is at all sane.
#
# uint64_t marquise_hash_identifier(const unsigned char *id, size_t id_len);
#for identifier in [ "foo", "" ]:
#	identifier_len = len(identifier)
#	hid = c_libmarquise.marquise_hash_identifier(cstring(identifier), identifier_len)
#	print(hid)


m = Marquise("mynamespace")
#print(m)
m.send_simple(42)
