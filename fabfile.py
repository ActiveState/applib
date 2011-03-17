# Copyright (c) 2010 ActiveState Software Inc. All rights reserved.

import sys
import os
import os.path as P
from fabric.api import *

# Import github.com/srid/fablib
sys.path.append(P.abspath(
    P.join(P.dirname(__file__), 'fablib')))
import venv
local = venv.local


clean = venv.clean
init = venv.init


def test(k=None):
    """Run tests"""
    venv.install('pytest')
    py_test = venv.get_script('py.test')
    test_script = P.join('applib', 'test', 'all.py')
    if not P.exists('tmp'):
        os.mkdir('tmp')
    if k is not None:
        args = " -k " + k
    else:
        args = ""
    local(
        '{0} -x -v {1} {2} --junitxml=tmp/testreport.xml'.format(py_test, test_script, args),
        capture=False)


def tox():
    """Run tox"""
    if not P.exists('tmp'):
        os.mkdir('tmp')
    venv.tox()
