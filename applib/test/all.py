import os
from os import path
import tempfile

from applib import sh, textui


def test_import():
    import applib
    import applib.base
    import applib.sh
    import applib.textui
    import applib.log
    import applib.misc


def test_console_width_detection():
    width = textui.find_console_width()
    assert width > 0
    

def test_colprint():
    sample_table = [
        ['python-daemon', '4.5.7.7.3-1', 'blah foo meh yuck'],
        ['foo',           '6.1', ('some very loooooooooong string here .. I '
                                  'suggest we make it even longer .. so longer '
                                  ' that normal terminal widths should entail '
                                  'colprint to trim the string')]]
    textui.colprint(sample_table)

    # try with empty inputs
    textui.colprint(None)
    textui.colprint([])

        
def test_compression_ensure_read_access():
    """Test the ensure_read_access() hack in _compression.py"""
    def test_pkg(pkgpath):
        testdir = tempfile.mkdtemp('-test', 'pypm-')
        extracted_dir, _ = sh.unpack_archive(pkgpath, testdir)
        # check if we have read access on the directory
        for child in os.listdir(extracted_dir):
            p = path.join(extracted_dir, child)
            if path.isdir(p):
                os.listdir(p)
        sh.rm(testdir)

    dr = path.join(path.dirname(__file__), 'fixtures')
    yield 'u-x on dirs', test_pkg, path.join(dr, 'generator_tools-0.3.5.tar.gz')
    yield 'u-w on ._setup.py', test_pkg, path.join(dr, 'TracProjectMenu-1.0.tar.gz')
    
