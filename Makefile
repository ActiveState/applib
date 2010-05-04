PYTHON := python

all: e installdeps

e:
	virtualenv --no-site-packages --distribute --python=${PYTHON} e
	e/bin/python -c 'assert "ActiveState" in str(__builtins__.copyright)'
	# e/bin/python -m activestate

installdeps:
	e/bin/python setup.py develop
	e/bin/pip install unittest2

test:
	e/bin/unit2 discover

clean:
	rm -rf e
