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


def require_option(options, option_name):
    """
    >>> require_option('foo-bar')
    ...
    CmdlnUserError: required option, --foo-bar, is mising
    """
    option_var_name = option_name.replace('-', '_')
    if getattr(options, option_var_name) is None:
        raise cmdln.CmdlnUserError, \
            'required option, --%s, is missing' % option_name