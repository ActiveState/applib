PYTHON := python

all: e installdeps

e:
	virtualenv --no-site-packages --distribute --python=${PYTHON} e
	e/bin/python -c 'assert "ActiveState" in str(__builtins__.copyright)'
	# e/bin/python -m activestate

installdeps:
	e/bin/python setup.py develop
	e/bin/pip install py

test:
	e/bin/py.test -x -v applib/test/all.py

clean:
	rm -rf e
