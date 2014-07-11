import os
import time
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

def len_cstring(new_string):
	# Assume UTF8 input
	return len(bytes(new_string, 'utf8'))

def is_cnull(maybe_null):
	return maybe_null == ffi.NULL

EINVAL = 2




# Throw libmarquise at CFFI, let it do the hard work. This gives us
# API-level access instead of ABI access, and is generally preferred.
c_libmarquise = ffi.verify("""#include "marquise.h" """, include_dirs=[marquise_file()], libraries=['marquise'] )


class Marquise(object):
	#typedef struct {
	#	char *spool_path_points;
	#	char *spool_path_contents;
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

		self.spool_path_points   = cprint(self.marquise_ctx.spool_path_points)
		self.spool_path_contents = cprint(self.marquise_ctx.spool_path_contents)

	def __str__(self):
		return "<Marquise handle spooling to {} and {}>".format(self.spool_path_points, self.spool_path_contents)

	def debug(self, msg):
		if self.debug_enabled:
			print("DEBUG: {}".format(msg))

	def close(self):
		self.debug("Shutting down Marquise handle spooling to {} and {}".format(self.spool_path_points, self.spool_path_contents))
		c_libmarquise.marquise_shutdown(self.marquise_ctx)
		# return None, shutdown always succeeds

	@staticmethod
	def hash_identifier(identifier):
		"""Performs siphash-2-4 on the input with a fixed all-zeroes key, returnval is an integer"""
		return c_libmarquise.marquise_hash_identifier(cstring(identifier), len(identifier) )
		# XXX: do I need to free anything here, or will stuff drop out
		# of scope cleanly and get cleaned up?

	@staticmethod
	def current_timestamp():
		return int(time.time() * 1000000000)

	def send_simple(self, address=None, source=None, timestamp=None, value=None):
		"""
		Queue a simple datapoint (i.e., a 64-bit word), returns
		True/False for success.
		"""

		if value is None:
			# This is dirty, but I don't feel like putting `value`
			# at the start of the arguments list.
			raise TypeError("You must supply a `value`.")
		if address is None and source is None:
			raise TypeError("You must supply either `address` or `source`.")
		if address and source:
			raise TypeError("You must supply `address` or `source`, not both.")

		if source:
			self.debug("Supplied source: {}".format(source))
		if address:
			self.debug("Supplied address: {}".format(address))

		if source:
			address = self.hash_identifier(source)
			self.debug("The address will be {}".format(address))

		# timestamp is nanoseconds since epoch
		if timestamp is None:
			timestamp = self.current_timestamp()

		# Wrap/convert our arguments to C datatypes before dispatching.
		# FFI will take care of converting them to the right endianness. I think.
		c_address =   ffi.cast("uint64_t", address)
		c_timestamp = ffi.cast("uint64_t", timestamp)
		c_value =     ffi.cast("uint64_t", value)

		retval = c_libmarquise.marquise_send_simple(self.marquise_ctx, c_address, c_timestamp, c_value)
		self.debug("send_simple retval is {}".format(retval))

		# XXX: Gotta free anything here? c_address/c_timestamp/c_value
		# will fall out of scope in a sec anyway.

		return True if retval == 0 else False

	# Simple wrappers to skip specifying address/source all the time
	def send_simple_source(self, source, timestamp, value):
		return self.send_simple(source=source, timestamp=timestamp, value=value)

	def send_simple_address(self, address, timestamp, value):
		return self.send_simple(address=address, timestamp=timestamp, value=value)


	def send_extended(self, address=None, source=None, timestamp=None, value=None):
		"""
		Queue an extended datapoint (ie. a string), returns True/False
		for success.
		"""

		if value is None:
			# This is dirty, but I don't feel like putting `value`
			# at the start of the arguments list.
			raise TypeError("You must supply a `value`.")
		if address is None and source is None:
			raise TypeError("You must supply either `address` or `source`.")
		if address and source:
			raise TypeError("You must supply `address` or `source`, not both.")

		if source:
			self.debug("Supplied source: {}".format(source))
		if address:
			self.debug("Supplied address: {}".format(address))

		if source:
			address = self.hash_identifier(source)
			self.debug("The address will be {}".format(address))

		# timestamp is nanoseconds since epoch
		if timestamp is None:
			timestamp = self.current_timestamp()

		# Will need to call ffi.new and stuff around here to make up the C datatypes and dispatch them.
		# FFI will take care of converting them to the right endianness. I think.
		c_address =   ffi.cast("uint64_t", address)
		c_timestamp = ffi.cast("uint64_t", timestamp)
		# c_value needs to be a byte array with a length in bytes
		c_value =     cstring(value)
		c_length =    ffi.cast("size_t", len_cstring(value))
		self.debug("Sending extended value '{}' with length of {}".format(value, c_length))

		retval = c_libmarquise.marquise_send_extended(self.marquise_ctx, c_address, c_timestamp, c_value, c_length);
		self.debug("send_extended retval is {}".format(retval))

		# XXX: Gotta free anything here? c_address/c_timestamp/c_value
		# will fall out of scope in a sec anyway.

		return True if retval == 0 else False



	def update_source(self, metadata_dict, address=None, source=None):
		"""
		Pack the incoming dict into a data structure, ship it off to
		the spool file, then free up your resources.  Raise an
		exception if anything goes wrong at any stage.
		"""

		if address is None and source is None:
			raise TypeError("You must supply either `address` or `source`.")
		if address and source:
			raise TypeError("You must supply `address` or `source`, not both.")

		if source:
			self.debug("Supplied source: {}".format(source))
		if address:
			self.debug("Supplied address: {}".format(address))

		if source:
			address = self.hash_identifier(source)
			self.debug("The address will be {}".format(address))


		# Sanity check the input, everything must be UTF8 strings (not
		# yet confirmed), no Nonetypes or anything stupid like that.
		#
		# XXX: The keys of the key-value pairs *must* be unique, right?
		# Well they will be now because it's a dict coming in.
		if any([ x is None for x in metadata_dict.keys() ]):
			raise TypeError("One of your metadata_dict keys is a Nonetype")
		if any([ x is None for x in metadata_dict.values() ]):
			raise TypeError("One of your metadata_dict values is a Nonetype")

		# Cast each string to a C-string
		# XXX: This will have unusual results if the inputs are
		# non-strings, eg. bools become a zero-length string and
		# numbers are also zero-length but get memory malloc'd
		# corresponding to their magnitude. Should probably pass
		# everything through str() first to sanitise.
		try:                   c_fields = [ cstring(x) for x in metadata_dict.keys() ]
		except Exception as e: raise TypeError("One of your metadata_dict keys couldn't be cast to a Cstring, {}".format(e))

		try:                   c_values = [ cstring(x) for x in metadata_dict.values() ]
		except Exception as e: raise TypeError("One of your metadata_dict values couldn't be cast to a Cstring, {}".format(e))


		# Get our source_dict data structure
		source_dict = c_libmarquise.marquise_new_source(c_fields, c_values, len(metadata_dict))
		if is_cnull(source_dict):
			raise ValueError("errno is set to EINVAL on invalid input, our errno is {}".format(ffi.errno))


		success = c_libmarquise.marquise_update_source(self.marquise_ctx, address, source_dict)
		self.debug("marquise_update_source returned {}".format(success))
		if success != 0:
			raise RuntimeError("marquise_update_source was unsuccessful, errno is {}".format(ffi.errno))
		c_libmarquise.marquise_free_source(source_dict)




# Test calling the hash function
test_identifier = "hostname:fe1.example.com,metric:BytesUsed,service:memory,"
sample_address = 5753895591108871589

print("This should print 7602883380529707052:")
print(Marquise.hash_identifier(test_identifier) )


# Test initialisation
m = Marquise("mynamespace", debug=True)
print(m)


# Test send_simple()
m.send_simple_address(5, 100, 200000)
m.send_simple_address(5, 101, 200001)
m.send_simple_address(5, 102, 200002)
m.send_simple_address(5, 103, 200003)

m.send_simple_source(test_identifier, None, 42)
m.send_simple_source("hostname:misaka.anchor.net.au,metric:BytesTx,service:network,", None, 42)
m.send_simple_source("hostname:misaka.anchor.net.au,metric:BytesTx,service:network,", None, 100)
m.send_simple_source("hostname:misaka.anchor.net.au,metric:BytesTx,service:network,", None, 9000)

m.send_extended(source="hostname:misaka.anchor.net.au", timestamp=None, value="foobar")
m.send_extended(source="hostname:misaka.anchor.net.au", timestamp=None, value="lorem ipsum")
m.send_extended(source="hostname:misaka.anchor.net.au", timestamp=None, value="dolor")
m.send_extended(source="hostname:misaka.anchor.net.au", timestamp=None, value="dolorite")
m.send_extended(source="hostname:misaka.anchor.net.au", timestamp=None, value="I love me some geology")


m.send_extended(address=sample_address, timestamp=None, value="Chasing paper")


# Jay mentioned something about calling your cleanup functions at the right
# time. It's good practice to call close() manually, but as a last-ditch
# measure you can attach close() to the object's deallocation hooks, with the
# caveat that this is *not* guaranteed to be actually run in a timely manner
# when del(yourObject) occurs.
m.close()
