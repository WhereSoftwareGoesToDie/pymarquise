cimport cmarquise

from errors import MarquiseException

cdef class Marquise:
	cdef cmarquise.marquise_consumer _c_consumer
	cdef cmarquise.marquise_connection _c_connection
	def __cinit__(self, broker, batch_period):
		cdef bytes broker_bytes = broker.encode()
		cdef char* c_broker = broker_bytes
		cdef double c_batch_period = batch_period
		self._c_consumer = cmarquise.marquise_consumer_new(c_broker, c_batch_period)
		if self._c_consumer is NULL:
			raise MarquiseException("marquise_consumer_new returned NULL")
		self._c_connection = cmarquise.marquise_connect(self._c_consumer)
		if self._c_connection is NULL:
			raise MarquiseException("marquise_connect returned NULL")
