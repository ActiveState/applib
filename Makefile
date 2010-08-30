PYTHON := python

all: e installdeps

e:
	virtualenv --no-site-packages --distribute --python=${PYTHON} .
	bin/python -c 'assert "ActiveState" in str(__builtins__.copyright)'
	# e/bin/python -m activestate

installdeps:
	bin/python setup.py develop
	bin/pip install py

test:
	bin/py.test -x -v applib/test/all.py --junitxml=tmp/testreport.xml

clean:
	rm -rf bin/ lib/ include/
