import sys
import os
from os import path
import tarfile
import zipfile
from contextlib import closing

from applib import sh

__all__ = ['implementors']


class CompressedFile(object):
    def __init__(self, filename):
        self.filename = filename
        

class ZippedFile(CompressedFile):
    """A zip file"""

    @staticmethod
    def is_valid(filename):
        return zipfile.is_zipfile(filename)

    def extract(self):
        try:
            f = zipfile.ZipFile(self.filename, 'r')
            try:
                f.extractall()
                return _possible_dir_name(f.namelist())
            except OSError:
                _, e, _ = sys.exc_info()
                if e.errno == 17:
                    # http://bugs.python.org/issue6510
                    raise sh.PackError(e)
                # http://bugs.python.org/issue6609
                if sys.platform.startswith('win'):
                    if isinstance(e, WindowsError) and e.winerror == 267:
                        raise sh.PackError('uses Windows special name (%s)' % e)
                raise
            finally:
                f.close()
        except (zipfile.BadZipfile, zipfile.LargeZipFile):
            _, e, _ = sys.exc_info()
            raise sh.PackError(e)

    @classmethod
    def pack(cls, paths, file):
        raise NotImplementedError('pack: zip files not supported yet')
    

class TarredFile(CompressedFile):
    """A tar.gz/bz2 file"""
    
    @classmethod
    def is_valid(cls, filename):
        try:
            with closing(tarfile.open(filename, cls._get_mode())) as f:
                return True
        except tarfile.TarError:
            return False

    def extract(self):
        try:
            f = tarfile.open(self.filename, self._get_mode())
            try:
                _ensure_read_write_access(f)
                f.extractall()
                return _possible_dir_name(f.getnames())
            finally:
                f.close()
        except tarfile.TarError:
            _, e, _ = sys.exc_info()
            raise sh.PackError(e)
        except IOError:
            _, e, _ = sys.exc_info()
            # see http://bugs.python.org/issue6584
            if 'CRC check failed' in str(e):
                raise sh.PackError(e)
            else:
                raise
            
    @classmethod
    def pack(cls, paths, file):
        f = tarfile.open(file, cls._get_mode('w'))
        try:
            for pth in paths:
                assert path.exists(pth), '"%s" does not exist' % path
                f.add(pth)
        finally:
            f.close()

    def _get_mode(self):
        """Return the mode for this tarfile"""
        raise NotImplementedError()


class GzipTarredFile(TarredFile):
    """A tar.gz2 file"""

    @staticmethod
    def _get_mode(mode='r'):
        assert mode in ['r', 'w']
        return mode + ':gz'


class Bzip2TarredFile(TarredFile):
    """A tar.gz2 file"""

    @staticmethod
    def _get_mode(mode='r'):
        assert mode in ['r', 'w']
        return mode + ':bz2'


implementors = dict(
    zip = ZippedFile,
    tgz = GzipTarredFile,
    bz2 = Bzip2TarredFile)


class MultipleTopLevels(sh.PackError):
    """Can be extracted, but contains multiple top-level dirs"""
class SingleFile(sh.PackError):
    """Contains nothing but a single file. Compressed archived is expected to
    contain one directory
    """
    

def _possible_dir_name(contents):
    """The directory where the the files are possibly extracted."""
    top_level_dirs = _find_top_level_directories(contents, sep='/')
    if len(top_level_dirs) == 0:
        raise sh.PackError('has no contents')
    elif len(top_level_dirs) > 1:
        raise MultipleTopLevels('more than one top levels: %s' % top_level_dirs)
    d = path.abspath(top_level_dirs[0])
    assert path.exists(d), 'missing dir: %s' % d
    if not path.isdir(d):
        # eg: http://pypi.python.org/pypi/DeferArgs/0.4
        raise SingleFile('contains a single file: %s' % d)
    return d


def _ensure_read_write_access(tarfileobj):
    """Ensure that the given tarfile will be readable and writable by the
    user (the client program using this API) after extraction.

    Some tarballs have u-x set on directories or u-w on files. We reset such
    perms here.. so that the extracted files remain accessible for reading
    and deletion as per the user's wish.

    See also: http://bugs.python.org/issue6196
    """
    dir_perm = tarfile.TUREAD | tarfile.TUWRITE | tarfile.TUEXEC
    file_perm = tarfile.TUREAD | tarfile.TUWRITE

    for tarinfo in tarfileobj.getmembers():
        tarinfo.mode |= (dir_perm if tarinfo.isdir() else file_perm)
        

def _find_top_level_directories(fileslist, sep):
    """Find the distinct first components in the fileslist"""
    toplevels = set()
    for pth in fileslist:
        firstcomponent = pth.split(sep, 1)[0]
        toplevels.add(firstcomponent)
    return list(toplevels)
    