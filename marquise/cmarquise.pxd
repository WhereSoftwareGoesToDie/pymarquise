from libc.stdint cimport uint64_t, int64_t, uint8_t

cdef extern from "marquise.h":
	ctypedef void* marquise_consumer
	ctypedef void* marquise_connection

	marquise_consumer marquise_consumer_new(char *broker, double batch_period)
	void marquise_consumer_shutdown(marquise_consumer consumer)
	
	marquise_connection marquise_connect(marquise_consumer consumer)
	void marquise_close(marquise_connection connection)

	int marquise_send_text(marquise_connection connection, char **source_fields,
			       char **source_values, size_t source_count, char *data,
			       size_t length
			       , uint64_t timestamp)
	
	int marquise_send_int(marquise_connection connection, char **source_fields,
			      char **source_values, size_t source_count, int64_t data
			      , uint64_t timestamp)
	
	int marquise_send_real(marquise_connection connection, char **source_fields,
			       char **source_values, size_t source_count, double data
			       , uint64_t timestamp)
	
	int marquise_send_counter(marquise_connection connection, char **source_fields,
				  char **source_values, size_t source_count
				  , uint64_t timestamp)
	
	int marquise_send_binary(marquise_connection connection, char **source_fields,
				 char **source_values, size_t source_count,
				 uint8_t * data, size_t length
				 , uint64_t timestamp)
