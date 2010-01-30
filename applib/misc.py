"""Miscelleneous utility functions
"""

from os import path

__all__ = ['xjoin', 'existing']


def xjoin(*c):
    """Equivalent to normpath(abspath(join(*c)))"""
    return path.normpath(path.abspath(path.join(*c)))


def existing(pth):
    """Return path, but assert its presence first"""
    assert isinstance(pth, (str, unicode)), \
        'not of string type: %s <%s>' % (pth, type(pth))
    assert exists(pth), 'file/directory not found: %s' % pth
    return pth