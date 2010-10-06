import sys
from os import path
from fabric.api import *

# Import github.com/srid/fablib
sys.path.append(path.abspath(
    path.join(path.dirname(__file__), 'fablib')))
import venv


clean = venv.clean
init = venv.init
