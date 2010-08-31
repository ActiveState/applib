PYTHON := python

all: createvenv installdeps

createvenv:
	virtualenv --no-site-packages --python=${PYTHON} .
	bin/easy_install -U distribute
	bin/python -m activestate > /dev/null # are we using activepython?

installdeps:
	bin/python setup.py develop
	bin/easy_install py

test:
	bin/py.test -x -v applib/test/all.py --junitxml=tmp/testreport.xml

clean:
	rm -rf bin/ lib/ include/
