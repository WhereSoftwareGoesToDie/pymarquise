cimport cmarquise

cdef class Marquise:
	cdef cmarquise.marquise_consumer _c_consumer
	cdef cmarquise.marquise_connection _c_connection
	def __cinit__(self, broker, batch_period):
		cdef bytes broker_bytes = broker.encode()
		cdef char* c_broker = broker_bytes
		cdef double c_batch_period = batch_period
		_c_consumer = cmarquise.marquise_consumer_new(c_broker, c_batch_period)
		_c_connection = cmarquise.marquise_connect(_c_consumer)
