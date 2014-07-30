# BUILDING: You will need cffi to make the bindings.
#
# TESTING: You need pytest and pytest-cov for testing and coverage
# respectively.

ext: clean
	python setup.py build_ext -if

run:
	MARQUISE_SPOOL_DIR=/tmp python -B marquise.py


# We make a bunch of assumptions about the pymarquise code that need testing.
# test_pymarquise.py does the work needed to satisfactorily exercise
# pymarquise, and an HTML coverage report is dumped into `htmlcov/`
test:
	MARQUISE_SPOOL_DIR=/tmp py.test --cov=marquise test_pymarquise.py --cov-report=html

# So we can verify that test_pymarquise.py satisfactorily covers 100% of the
# pymarquise code, but how do we know that all of test_pymarquise.py is getting
# run? With more tests! This target produces a coverage report about
# test_pymarquise.py, dumping it in `htmlcov/`
test-coverage-of-main-in-testsuite:
	MARQUISE_SPOOL_DIR=/tmp coverage run test_pymarquise.py ; coverage html test_pymarquise.py

# You should run this before switching between the two kinds of test above.
# This is necessary because you can get cross-contamination between them.
testclean:
	-rm -f .coverage
	-rm -rf htmlcov/


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
