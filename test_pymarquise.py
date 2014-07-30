# pylint: disable=line-too-long
# pylint: disable=bad-whitespace
# I just like to watch the world burn:
# pylint: disable=mixed-indentation
# pylint: disable=invalid-name

"""This should be a comprehensive testsuite for Pymarquise's functionality."""

import sys
import os
import pytest
from marquise import Marquise

# This keeps pylint happy
# pylint: disable=no-member
RAISES = pytest.raises
# pylint: enable=no-member

TEST_GOOD_NAMESPACE     = "mytestnamespace"
TEST_BAD_NAMESPACE      = "3v1l_L33T_BaD_nAmEsPaCe!!!!!!"
TEST_TOO_LONG_NAMESPACE = "thisisaverylongnamespacenamethatislongerthan256charactersbecausethatisallthatisallowedforafilenameinlinux000inthelightofthemoonalittleegglayonaleaf000onesundaymorningthewarmsuncameupandpopoutoftheeggcameatinyandveryhungrycaterpillar000hestartedtolookforsomefood"

TEST_GOOD_ADDRESS    = 5753895591108871589
TEST_BAD_ADDRESS     = "HA HA I'M USING THE INTERNET"

TEST_IDENTIFIER      = "hostname:fe1.example.com,metric:BytesUsed,service:memory,"
TEST_SOURCE1         = "hostname:misaka.anchor.net.au,metric:BytesTx,service:network,"
TEST_SOURCE2         = "hostname:misaka.anchor.net.au"

TEST_GOOD_SOURCE_DICT          = { 'foofoofoo':"barbarbar", 'lolololol':"catte",    'something else altogether':"that is rather long indeed", 'test':"source_dict" }
TEST_BAD_SOURCE_DICT_NONE_KEY  = { None:"barbarbar",        'trolololol':"catte",   'something else altogether':"that is rather long indeed", 'test':"source_dict" }
TEST_BAD_SOURCE_DICT_NONE_VAL  = { "foofoofoo":"barbarbar", 'trolololol':None,      'something else altogether':"that is rather long indeed", 'test':"source_dict" }
TEST_BAD_SOURCE_DICT_EXC_KEY   = { Exception:"barbarbar",   'trolololol':"catte",   'something else altogether':"that is rather long indeed", 'test':"source_dict" }
TEST_BAD_SOURCE_DICT_EXC_VAL   = { 'foofoofoo':Exception,   'trolololol':"catte",   'something else altogether':"that is rather long indeed", 'test':"source_dict" }
TEST_BAD_SOURCE_DICT_COLON_KEY = { 'foo:::foo':"barbarbar", 'trolololol':"catte",   'something else altogether':"that is rather long indeed", 'test':"source_dict" }
TEST_BAD_SOURCE_DICT_COLON_VAL = { 'foofoofoo':"bar:::bar", 'trolololol':"catte",   'something else altogether':"that is rather long indeed", 'test':"source_dict" }

DEBUG = False


def test_yo_dawg_i_heard_you_liek_tests():
	"""Ensure that the "bad" input to another test function is indeed bad enough."""
	assert len(TEST_TOO_LONG_NAMESPACE) > 256

def test_hash_identifier():
	"""Ensure that we can call hash_identifier and get the right answer back."""
	assert Marquise.hash_identifier(TEST_IDENTIFIER) == 7602883380529707052

def test_bogus_namespace():
	"""Ensure that invalid namespaces are not accepted."""
	with RAISES(ValueError):
		# pylint: disable=unused-variable
		marq = Marquise(TEST_BAD_NAMESPACE, debug=DEBUG)
		# pylint: enable=unused-variable

def test_very_very_very_long_namespace():
	"""Ensure that a too-long namespace is not accepted."""
	with RAISES(RuntimeError) as excinfo:
		# pylint: disable=unused-variable
		marq = Marquise(TEST_TOO_LONG_NAMESPACE, debug=DEBUG)
		# pylint: enable=unused-variable
	assert excinfo.value.args[0].endswith("errno is 36")

def test_print_a_marquise_with_debugging():
	"""Ensure that the Marquise class' __str__ method doesn't explode."""
	print("-"*72)
	marq = Marquise(TEST_GOOD_NAMESPACE, debug=True)
	print(marq)
	marq.close()
	print("-"*72)



def test_send_simple():
	"""Exercise send_simple with good and bad input."""
	marq = Marquise(TEST_GOOD_NAMESPACE, debug=DEBUG)
	# Normal use specifying address directly
	assert marq.send_simple(address=TEST_GOOD_ADDRESS, timestamp=None, value=42)
	assert marq.send_simple(address=TEST_GOOD_ADDRESS, timestamp=1234567890, value=42)
	# Non-numeric and not-None timestamp
	with RAISES(TypeError):
		assert marq.send_simple(address=TEST_GOOD_ADDRESS, timestamp="pantsu", value=42)
	# Non-numeric value
	with RAISES(TypeError):
		marq.send_simple(address=TEST_GOOD_ADDRESS, timestamp=None, value="pantsu")
	# Non-numeric address
	with RAISES(TypeError):
		marq.send_simple(address=TEST_SOURCE1, timestamp=None, value=42)
	# None as a value
	with RAISES(TypeError):
		assert marq.send_simple(address=TEST_GOOD_ADDRESS, timestamp=None, value=None)
	marq.close()


def test_send_simple_after_close():
	"""Ensure that send_simple explodes if you attempt to use a closed handle."""
	marq = Marquise(TEST_GOOD_NAMESPACE, debug=DEBUG)
	marq.close()
	with RAISES(ValueError):
		marq.send_simple(address=TEST_GOOD_ADDRESS, timestamp=None, value=42)
	assert marq.close() is None


def test_send_simple_write_failure():
	"""Ensure that send_simple explodes if the write fails."""
	marq = Marquise(TEST_GOOD_NAMESPACE, debug=DEBUG)
	# Cause the write to fail due to the file being read-only.
	os.chmod(marq.spool_path_points, 0o400)
	with RAISES(RuntimeError) as excinfo:
		marq.send_simple(address=TEST_GOOD_ADDRESS, timestamp=None, value=42)
	assert excinfo.value.args[0].endswith("errno is 13")
	marq.close()


def test_send_extended():
	"""Exercise send_simple with good and bad input."""
	marq = Marquise(TEST_GOOD_NAMESPACE, debug=DEBUG)
	# Normal use specifying address directly
	assert marq.send_extended(address=TEST_GOOD_ADDRESS, timestamp=None, value="lorem ipsum")
	assert marq.send_extended(address=TEST_GOOD_ADDRESS, timestamp=1234567890, value="dolor")
	# Non-numeric and not-None timestamp
	with RAISES(TypeError):
		assert marq.send_extended(address=TEST_GOOD_ADDRESS, timestamp="pantsu", value="dolorite")
	# Non-numeric address
	with RAISES(TypeError):
		assert marq.send_extended(address=TEST_SOURCE1, timestamp=None, value="I love me some geology")
	# None as a value
	with RAISES(TypeError):
		assert marq.send_extended(address=TEST_GOOD_ADDRESS, timestamp=None, value=None)
	marq.close()


def test_send_extended_after_close():
	"""Ensure that send_extended explodes if you attempt to use a closed handle."""
	marq = Marquise(TEST_GOOD_NAMESPACE, debug=DEBUG)
	marq.close()
	with RAISES(ValueError):
		marq.send_extended(address=TEST_GOOD_ADDRESS, timestamp=None, value="This is a closed handle.")
	assert marq.close() is None


def test_send_extended_write_failure():
	"""Ensure that send_extended explodes if the write fails."""
	marq = Marquise(TEST_GOOD_NAMESPACE, debug=DEBUG)
	# Cause the write to fail due to the file being read-only.
	os.chmod(marq.spool_path_points, 0o400)
	with RAISES(RuntimeError) as excinfo:
		marq.send_extended(address=TEST_GOOD_ADDRESS, timestamp=None, value=42)
	assert excinfo.value.args[0].endswith("errno is 13")
	marq.close()


def test_update_source():
	"""Exercise update_source with good and bad input."""
	marq = Marquise(TEST_GOOD_NAMESPACE, debug=DEBUG)
	# Normal use
	assert marq.update_source(TEST_GOOD_ADDRESS, TEST_GOOD_SOURCE_DICT)
	# Non-numeric address
	with RAISES(TypeError):
		marq.update_source(TEST_BAD_ADDRESS, TEST_GOOD_SOURCE_DICT)
	# Keys and values set to None
	with RAISES(TypeError):
		marq.update_source(TEST_GOOD_ADDRESS, TEST_BAD_SOURCE_DICT_NONE_KEY)
	with RAISES(TypeError):
		marq.update_source(TEST_GOOD_ADDRESS, TEST_BAD_SOURCE_DICT_NONE_VAL)
	# Keys and values set to Exception, a Python class that can't be cast to anything C
	with RAISES(TypeError):
		marq.update_source(TEST_GOOD_ADDRESS, TEST_BAD_SOURCE_DICT_EXC_KEY)
	with RAISES(TypeError):
		marq.update_source(TEST_GOOD_ADDRESS, TEST_BAD_SOURCE_DICT_EXC_VAL)
	# Keys and values containing colons, which are invalid
	with RAISES(ValueError):
		marq.update_source(TEST_GOOD_ADDRESS, TEST_BAD_SOURCE_DICT_COLON_KEY)
	with RAISES(ValueError):
		marq.update_source(TEST_GOOD_ADDRESS, TEST_BAD_SOURCE_DICT_COLON_VAL)
	marq.close()


def test_update_source_after_close():
	"""Ensure that update_source explodes if you attempt to use a closed handle."""
	marq = Marquise(TEST_GOOD_NAMESPACE, debug=DEBUG)
	marq.close()
	with RAISES(ValueError):
		marq.update_source(TEST_GOOD_ADDRESS, TEST_GOOD_SOURCE_DICT)
	assert marq.close() is None


def test_update_source_write_failure():
	"""Ensure that update_source explodes if the write fails."""
	marq = Marquise(TEST_GOOD_NAMESPACE, debug=DEBUG)
	# Cause the write to fail due to the file being read-only.
	os.chmod(marq.spool_path_contents, 0o400)
	with RAISES(RuntimeError) as excinfo:
		marq.update_source(TEST_GOOD_ADDRESS, TEST_GOOD_SOURCE_DICT)
	assert excinfo.value.args[0].endswith("errno is 13")
	marq.close()


def test_double_close_okay():
	"""Ensure that double-close() is safe, it should be a no-op."""
	marq = Marquise(TEST_GOOD_NAMESPACE, debug=DEBUG)
	marq.close()
	assert marq.close() is None



if __name__ == '__main__':
	# It's nicer to put it all in here.
	os.environ['MARQUISE_SPOOL_DIR'] = '/tmp'

	test_yo_dawg_i_heard_you_liek_tests()
	test_hash_identifier()
	test_bogus_namespace()
	test_very_very_very_long_namespace()
	test_print_a_marquise_with_debugging()

	test_send_simple()
	test_send_simple_after_close()
	test_send_simple_write_failure()

	test_send_extended()
	test_send_extended_after_close()
	test_send_extended_write_failure()

	test_update_source()
	test_update_source_after_close()
	test_update_source_write_failure()

	test_double_close_okay()

	sys.exit(0)
