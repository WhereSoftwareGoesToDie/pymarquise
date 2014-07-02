run:
	MARQUISE_SPOOL_DIR=/tmp python -B marquise.py

build_ext:
	MARQUISE_SPOOL_DIR=/tmp python setup.py build_ext -if

clean:
	-rm -rf __pycache__/
	-rm -rf build/
	-rm _cffi__*.so
	find . -name '*.pyc' -delete
