# Written to target Python 3.x exclusively.

import time
from .marquise_cffi import  ffi, EINVAL, cprint, cstring, len_cstring, is_cnull, c_libmarquise
class Marquise(object):

	"""
	This libmarquise binding provides an interface to submit simple and
	extended datapoints, and provide "source dictionaries" containing
	metadata about datapoints.
	"""

	def __init__(self, namespace, debug=False):
		"""Establish a marquise context for the provided namespace,
		getting spool filenames.

		Arguments:
		namespace -- must be lowercase alphanumeric ([a-z0-9]+).
		debug -- if debug is True, debugging output will be printed.
		"""
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
		"""Return a human-readable description of the current Marquise context."""
		return "<Marquise handle spooling to {} and {}>".format(self.spool_path_points, self.spool_path_contents)

	def __debug(self, msg):
		"""Print `msg` if debugging is enabled on this instance. Intended for internal use."""
		if self.debug_enabled:
			print("DEBUG: {}".format(msg))

	def close(self):
		"""Close the Marquise context, ensuring data is flushed and
		spool files are closed.

		This should always be closed explicitly, as there's no
		guarantees that it will happen when the instance is deleted.
		"""
		self.__debug("Shutting down Marquise handle spooling to {} and {}".format(self.spool_path_points, self.spool_path_contents))
		c_libmarquise.marquise_shutdown(self.marquise_ctx)

	@staticmethod
	def hash_identifier(identifier):
		"""Return the siphash-2-4 of the `identifier`, using a static
		all-zeroes key.

		The output is an integer, which is used as the `address` of
		datapoints belonging to the given `identifier` string.
		"""
		return c_libmarquise.marquise_hash_identifier(cstring(identifier), len(identifier) )
		# XXX: do I need to free anything here, or will stuff drop out
		# of scope cleanly and get cleaned up?

	@staticmethod
	def current_timestamp():
		"""Return the current timestamp, nanoseconds since epoch."""
		return int(time.time() * 1000000000)

	def send_simple(self, address=None, source=None, timestamp=None, value=None):
		"""Queue a simple datapoint (i.e., a 64-bit word), returns True/False for success."""

		if value is None:
			# This is dirty, but I don't feel like putting `value`
			# at the start of the arguments list.
			raise TypeError("You must supply a `value`.")
		if address is None and source is None:
			raise TypeError("You must supply either `address` or `source`.")
		if address and source:
			raise TypeError("You must supply `address` or `source`, not both.")

		if source:
			self.__debug("Supplied source: {}".format(source))
		if address:
			self.__debug("Supplied address: {}".format(address))

		if source:
			address = self.hash_identifier(source)
			self.__debug("The address will be {}".format(address))

		if timestamp is None:
			timestamp = self.current_timestamp()

		# Wrap/convert our arguments to C datatypes before dispatching.
		# FFI will take care of converting them to the right endianness. I think.
		c_address =   ffi.cast("uint64_t", address)
		c_timestamp = ffi.cast("uint64_t", timestamp)
		c_value =     ffi.cast("uint64_t", value)

		retval = c_libmarquise.marquise_send_simple(self.marquise_ctx, c_address, c_timestamp, c_value)
		self.__debug("send_simple retval is {}".format(retval))

		# XXX: Gotta free anything here? c_address/c_timestamp/c_value
		# will fall out of scope in a sec anyway.

		return True if retval == 0 else False

	# Simple wrappers to skip specifying address/source all the time
	def send_simple_source(self, source, timestamp, value):
		"""Given a textual `source`, call send_simple() appropriately."""
		return self.send_simple(source=source, timestamp=timestamp, value=value)

	def send_simple_address(self, address, timestamp, value):
		"""Given `address` (a siphash-2-4 integer), call send_simple() appropriately."""
		return self.send_simple(address=address, timestamp=timestamp, value=value)


	def send_extended(self, address=None, source=None, timestamp=None, value=None):
		"""Queue an extended datapoint (ie. a string), returns True/False for success."""
		if value is None:
			# This is dirty, but I don't feel like putting `value`
			# at the start of the arguments list.
			raise TypeError("You must supply a `value`.")
		if address is None and source is None:
			raise TypeError("You must supply either `address` or `source`.")
		if address and source:
			raise TypeError("You must supply `address` or `source`, not both.")

		if source:
			self.__debug("Supplied source: {}".format(source))
		if address:
			self.__debug("Supplied address: {}".format(address))

		if source:
			address = self.hash_identifier(source)
			self.__debug("The address will be {}".format(address))

		if timestamp is None:
			timestamp = self.current_timestamp()

		# Will need to call ffi.new and stuff around here to make up the C datatypes and dispatch them.
		# FFI will take care of converting them to the right endianness. I think.
		c_address =   ffi.cast("uint64_t", address)
		c_timestamp = ffi.cast("uint64_t", timestamp)
		# c_value needs to be a byte array with a length in bytes
		c_value =     cstring(value)
		c_length =    ffi.cast("size_t", len_cstring(value))
		self.__debug("Sending extended value '{}' with length of {}".format(value, c_length))

		retval = c_libmarquise.marquise_send_extended(self.marquise_ctx, c_address, c_timestamp, c_value, c_length);
		self.__debug("send_extended retval is {}".format(retval))

		# XXX: Gotta free anything here? c_address/c_timestamp/c_value
		# will fall out of scope in a sec anyway.

		return True if retval == 0 else False



	def update_source(self, metadata_dict, address=None, source=None):
		"""Pack `metadata_dict` into a data structure and ship it to the spool file."""
		if address is None and source is None:
			raise TypeError("You must supply either `address` or `source`.")
		if address and source:
			raise TypeError("You must supply `address` or `source`, not both.")

		if source:
			self.__debug("Supplied source: {}".format(source))
		if address:
			self.__debug("Supplied address: {}".format(address))

		if source:
			address = self.hash_identifier(source)
			self.__debug("The address will be {}".format(address))

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
		self.__debug("marquise_update_source returned {}".format(success))
		if success != 0:
			raise RuntimeError("marquise_update_source was unsuccessful, errno is {}".format(ffi.errno))
		c_libmarquise.marquise_free_source(source_dict)
