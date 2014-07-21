# Need to specify the MARQUISE_SPOOL_DIR while I'm testing, I think.

ext: clean
	python setup.py build_ext -if

run:
	MARQUISE_SPOOL_DIR=/tmp python -B marquise.py

clean:
	-rm -rf __pycache__/
	-rm -rf marquise/__pycache__/
	-rm -rf build/
	-rm -rf dist
	-rm -rf marquise.egg-info
	-rm _cffi__*.so
	-rm *.cpython-34m.so
	find . -name '*.pyc' -delete
	@echo
	@echo
