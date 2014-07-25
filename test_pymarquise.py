import sys
import os
import pytest
from marquise import Marquise

TEST_GOOD_NAMESPACE     = "mytestnamespace"
TEST_BAD_NAMESPACE      = "3v1l_L33T_BaD_nAmEsPaCe!"
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
	assert len(TEST_TOO_LONG_NAMESPACE) > 256

def test_hash_identifier():
	assert Marquise.hash_identifier(TEST_IDENTIFIER) == 7602883380529707052

def test_bogus_namespace():
	with pytest.raises(ValueError):
		m = Marquise(TEST_BAD_NAMESPACE, debug=DEBUG)

def test_very_very_very_long_namespace():
	with pytest.raises(RuntimeError) as excinfo:
		m = Marquise(TEST_TOO_LONG_NAMESPACE, debug=DEBUG)
	assert excinfo.value.args[0].endswith("errno is 36")

def test_print_a_marquise_with_debugging():
	m = Marquise(TEST_GOOD_NAMESPACE, debug=True)
	print(m)
	m.close()




def test_send_simple():
	m = Marquise(TEST_GOOD_NAMESPACE, debug=DEBUG)
	# Normal use specifying address directly
	assert m.send_simple(address=TEST_GOOD_ADDRESS, value=42)
	# Non-simple value
	with pytest.raises(TypeError):
		m.send_simple(address=TEST_GOOD_ADDRESS, value="pantsu")
	# Non-numeric address
	with pytest.raises(TypeError):
		m.send_simple(address=TEST_SOURCE1, value=42)
	# Normal use with textual source
	assert m.send_simple(source=TEST_SOURCE1, value=42)
	m.close()


def test_send_simple_address():
	m = Marquise(TEST_GOOD_NAMESPACE, debug=DEBUG)
	assert m.send_simple_address(5, 100, 200000)
	assert m.send_simple_address(5, 101, 200001)
	assert m.send_simple_address(5, 102, 200002)
	assert m.send_simple_address(5, 103, 200003)
	m.close()


def test_send_simple_source():
	m = Marquise(TEST_GOOD_NAMESPACE, debug=DEBUG)
	assert m.send_simple_source(TEST_IDENTIFIER, None, 42)
	assert m.send_simple_source(TEST_SOURCE1,    None, 42)
	assert m.send_simple_source(TEST_SOURCE1,    None, 100)
	assert m.send_simple_source(TEST_SOURCE1,    None, 9000)
	m.close()


def test_send_simple_after_close():
	m = Marquise(TEST_GOOD_NAMESPACE, debug=DEBUG)
	m.close()
	with pytest.raises(ValueError):
		m.send_simple(address=TEST_GOOD_ADDRESS, value=42)
	assert m.close() is None


def test_how_do_i_even_call_send_simple_omg():
	m = Marquise(TEST_GOOD_NAMESPACE, debug=DEBUG)
	with pytest.raises(TypeError):
		m.send_simple(source="pantsu", timestamp=None, value=None)
	with pytest.raises(TypeError):
		m.send_simple(source=None, address=None, timestamp=None, value="pantsu")
	with pytest.raises(TypeError):
		m.send_simple(source="polka dots", address="stripes", timestamp=None, value="pantsu")
	m.close()




def test_send_extended():
	m = Marquise(TEST_GOOD_NAMESPACE, debug=DEBUG)
	assert m.send_extended(source=TEST_SOURCE2, timestamp=None, value="foobar")
	assert m.send_extended(source=TEST_SOURCE2, timestamp=None, value="lorem ipsum")
	assert m.send_extended(source=TEST_SOURCE2, timestamp=None, value="dolor")
	assert m.send_extended(source=TEST_SOURCE2, timestamp=None, value="dolorite")
	assert m.send_extended(source=TEST_SOURCE2, timestamp=None, value="I love me some geology")
	assert m.send_extended(address=TEST_GOOD_ADDRESS, timestamp=None, value="Chasing paper")
	m.close()
	with pytest.raises(ValueError):
		m.send_extended(address=TEST_GOOD_ADDRESS, value="This is a closed handle.")
	assert m.close() is None


def test_i_cannot_even_send_extended_wtf():
	m = Marquise(TEST_GOOD_NAMESPACE, debug=DEBUG)
	with pytest.raises(TypeError):
		m.send_extended(source="pantsu", timestamp=None, value=None)
	with pytest.raises(TypeError):
		m.send_extended(source=None, address=None, timestamp=None, value="pantsu")
	with pytest.raises(TypeError):
		m.send_extended(source="polka dots", address="stripes", timestamp=None, value="pantsu")
	m.close()


def test_update_source():
	m = Marquise(TEST_GOOD_NAMESPACE, debug=DEBUG)
	assert m.update_source(TEST_GOOD_SOURCE_DICT, address=TEST_GOOD_ADDRESS)
	with pytest.raises(TypeError):
		m.update_source(TEST_GOOD_SOURCE_DICT, address=TEST_BAD_ADDRESS)

	assert m.update_source(TEST_GOOD_SOURCE_DICT, source=TEST_IDENTIFIER)

	with pytest.raises(TypeError):
		m.update_source(TEST_BAD_SOURCE_DICT_NONE_KEY, address=TEST_GOOD_ADDRESS)
	with pytest.raises(TypeError):
		m.update_source(TEST_BAD_SOURCE_DICT_NONE_VAL, address=TEST_GOOD_ADDRESS)

	with pytest.raises(TypeError):
		m.update_source(TEST_BAD_SOURCE_DICT_EXC_KEY, address=TEST_GOOD_ADDRESS)
	with pytest.raises(TypeError):
		m.update_source(TEST_BAD_SOURCE_DICT_EXC_VAL, address=TEST_GOOD_ADDRESS)

	with pytest.raises(ValueError):
		m.update_source(TEST_BAD_SOURCE_DICT_COLON_KEY, address=TEST_GOOD_ADDRESS)
	with pytest.raises(ValueError):
		m.update_source(TEST_BAD_SOURCE_DICT_COLON_VAL, address=TEST_GOOD_ADDRESS)

	# Cleanly close.
	m.close()
	# Detonate it.
	with pytest.raises(ValueError):
		m.update_source(TEST_GOOD_SOURCE_DICT, address=TEST_GOOD_ADDRESS)
	# Double-close is safe.
	assert m.close() is None


def test_update_source_write_failure():
	m = Marquise(TEST_GOOD_NAMESPACE, debug=DEBUG)
	# Cause the write to fail due to the file being read-only.
	os.chmod(m.spool_path_contents, 0o400)
	with pytest.raises(RuntimeError) as excinfo:
		m.update_source(TEST_GOOD_SOURCE_DICT, address=TEST_GOOD_ADDRESS)
	assert excinfo.value.args[0].endswith("errno is 13")
	m.close()


def test_i_have_no_idea_what_i_am_doing_with_update_source():
	m = Marquise(TEST_GOOD_NAMESPACE, debug=DEBUG)
	with pytest.raises(TypeError):
		m.update_source(TEST_GOOD_SOURCE_DICT, source=None, address=None)
	with pytest.raises(TypeError):
		m.update_source(TEST_GOOD_SOURCE_DICT, source="polka dots", address="stripes")
	m.close()



if __name__ == '__main__':
	# It's nicer to put it all in here.
	os.environ['MARQUISE_SPOOL_DIR'] = '/tmp'

	test_yo_dawg_i_heard_you_liek_tests()
	test_hash_identifier()
	test_bogus_namespace()
	test_very_very_very_long_namespace()
	test_print_a_marquise_with_debugging()
	test_send_simple()
	test_send_simple_address()
	test_send_simple_source()
	test_send_simple_after_close()
	test_how_do_i_even_call_send_simple_omg()
	test_send_extended()
	test_i_cannot_even_send_extended_wtf()
	test_update_source()
	test_update_source_write_failure()
	test_i_have_no_idea_what_i_am_doing_with_update_source()

	sys.exit(0)
