PYTHON := python

all: e installdeps

e:
	virtualenv --distribute --python=${PYTHON} e
	e/bin/python -m activestate

installdeps:
	e/bin/python setup.py develop

clean:
	rm -rf e
