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
	#	char *spool_path;
	#	FILE *spool;
	#} marquise_ctx;

	#typedef struct {
	#	char **fields;
	#	char **values;
	#	size_t n_tags;
	#} marquise_source;

	def __init__(self, namespace, debug=False):
		self.debug_enabled = debug
		self.namespace_c = cstring(namespace)
		self.marquise_ctx = c_libmarquise.marquise_init(self.namespace_c)
		if is_cnull(self.marquise_ctx):
			if ffi.errno == EINVAL:
				raise ValueError("Invalid namespace: {}".format(namespace))
			raise RuntimeError("Something went wrong, got NULL instead of a marquise_ctx. build_spool_path() failed, or malloc failed. errno is {}".format(ffi.errno))

		self.spool_path = cprint(self.marquise_ctx.spool_path)

	def __str__(self):
		return "<Marquise handle spooling to {}>".format(self.spool_path)

	def debug(self, msg):
		if self.debug_enabled:
			print("DEBUG: {}".format(msg))

	def close(self):
		self.debug("Shutting down Marquise handle spooling to {}".format(self.spool_path))
		c_libmarquise.marquise_shutdown(self.marquise_ctx)
		# return None, shutdown always succeeds

	@staticmethod
	def hash_identifier(identifier):
		"""Performs siphash-2-4 on the input with a fixed all-zeroes key, returnval is an integer"""
		return c_libmarquise.marquise_hash_identifier(cstring(identifier), len(identifier) )
		# XXX: do I need to free anything here, or will stuff drop out
		# of scope cleanly and get cleaned up?

	def send_simple(self, address, timestamp, value):
		"""
		Queue a simple datapoint (i.e., a 64-bit word) to be sent by 
		the Marquise daemon. Returns zero on success and nonzero on 
		failure.

		int marquise_send_simple(marquise_ctx *ctx, uint64_t address, uint64_t timestamp, uint64_t value);
		"""
		# will need to call ffi.new and stuff around here to make up the C datatypes and dispatch them.
		c_address =   ffi.cast("int", address)
		c_timestamp = ffi.cast("int", timestamp)
		c_value =     ffi.cast("int", value)

		retval = c_libmarquise.marquise_send_simple(self.marquise_ctx, c_address, c_timestamp, c_value)
		self.debug("send_simple retval is {}".format(retval))
		# XXX: gotta free anything here?
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

	def new_source(self, FOO):
		# Not yet implemented, may be a different sort of class
		#marquise_source *marquise_new_source(char **fields, char **values, size_t n_tags);
		pass

	def update_source(self, FOO):
		# Not yet implemented, may be a different sort of class
		#int marquise_update_source(marquise_ctx *ctx, uint64_t address, marquise_source *source);
		pass

	def free_source(self, FOO):
		# Not yet implemented, may be a different sort of class
		#void marquise_free_source(marquise_source *source);
		pass


# Test calling the hash function
test_identifier = "hostname:fe1.example.com,metric:BytesUsed,service:memory,"
# Should print 7602883380529707052
print(Marquise.hash_identifier(test_identifier) )


# Test initialisation
m = Marquise("mynamespace", debug=True)
print(m)


# Test send_simple()
m.send_simple(5, 100, 200000)
m.send_simple(5, 101, 200001)
m.send_simple(5, 102, 200002)
m.send_simple(5, 103, 200003)


# Jay mentioned something about calling your cleanup functions at the right
# time. It's good practice to call close() manually, but as a last-ditch
# measure you can attach close() to the object's deallocation hooks, with the
# caveat that this is *not* guaranteed to be actually run in a timely manner
# when del(yourObject) occurs.
m.close()
del(m)
