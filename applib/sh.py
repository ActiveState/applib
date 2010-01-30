"""Various shell related wrappers
"""

from os import path
from contextlib import contextmanager

from applib._proc import *


#
# Compression routines
#

class PackError(Exception):
    """Error during pack or unpack"""
    

def unpack_archive(filename, path='.'):
    """Unpack the archive under ``path``
    
    Return (unpacked directory path, filetype)
    """
    from applib import _compression
    
    assert path.isfile(filename)
    assert path.isdir(path)
    
    for x in _compression.implementors.values():
        if x.is_valid(filename):
            with cd(path):
                return (x(filename).extract(), x)
    else:
        raise PackError, 'unknown compression format: ' + filename


def pack_archive(filename, files, pwd, filetype="tgz"):
    """Pack the given `files` from directory `pwd`
    
    `filetype` must be one of ["tgz", "tbz2", "zip"]
    """
    from applib import _compression
    
    assert isdir(pwd)
    assert filetype in _compression.implementors
    
    if path.exists(filename):
        rm(filename)
        
    with cd(pwd):
        relnames = [path.relpath(file, cwd) for file in files]
        _compression.implementors[filetype].pack(relnames, filename)
        

#
# Path/file routines
#

def mkdirs(path):
    """Make all directories along ``path``"""
    os.makedirs(path)
    
    
def rm(p):
    """Remove the specified path recursively. Similar to `rm -rf`"""
    if path.exists(p):
        if path.isdir(p):
            shutil.rmtree(p)
        else:
            os.remove(p)

    
def mv(src, dest, _mkdirs=False):
    """Move `src` to `dest`"""
    if _mkdirs:
        mkdirs(path.dirname(dest))
    shutil.move(src, dest)
    

def cp(src, dest, _mkdirs=False, ignore=None, copyperms=True):
    """Copy `src` to `dest` recursively"""
    assert path.exists(src)
    
    if _mkdirs:
        mkdirs(path.dirname(dest))
    
    if path.isdir(src):
        _copytree(src, dest, ignore=ignore, copyperms=copyperms)
    else:
        shutil.copyfile(src, dest)
    
    
@contextmanager
def cd(path):
    """With context to temporarily change directory"""
    assert path.isdir(path)
    
    cwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(cwd)



def _copytree(src, dst, symlinks=False, ignore=None, copyperms=True):
    """Forked shutil.copytree for `copyperms` support"""
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    os.makedirs(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                _copytree(srcname, dstname, symlinks, ignore, copyperms)
            else:
                shutil.copy(srcname, dstname)
            # XXX What about devices, sockets etc.?
        except (IOError, os.error), why:
            raise
            errors.append((srcname, dstname, str(why)))
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except shutil.Error, err:
            errors.extend(err.args[0])
    if copyperms:
        try:
            shutil.copystat(src, dst)
        except WindowsError:
            # can't copy file access times on Windows
            pass
        except OSError, why:
            errors.extend((src, dst, str(why)))
    if errors:
        raise shutil.Error, errors
    

# WindowsError is not available on other platforms
try:
    WindowsError
except NameError:
    class WindowsError(OSError): pass
