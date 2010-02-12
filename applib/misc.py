"""Miscelleneous utility functions
"""

import sys
from os import path

from applib import _cmdln as cmdln

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


def require_option(options, option_name, details=None):
    """
    >>> require_option('foo-bar')
    ...
    CmdlnUserError: required option, --foo-bar, is mising
    """
    option_var_name = option_name.replace('-', '_')
    if getattr(options, option_var_name) is None:
        msg = 'required option "--$s" is missing' % option_name
        if details:
            msg = '%s (%s)' % (msg, details)
        raise cmdln.CmdlnUserError, details
    
    
def _hack_unix2win_path_conversion(cmdln_options, option_names):
    """Hack to convert Unix paths in cmdln options (via config file) to
    Windows specific netshare location
    
    Config file must define the mapping as config var "unix2win_path_mapping"
    """
    require_option(cmdln_options, 'unix2win_path_mapping')
    
    for opt in option_names:
        setattr(
            cmdln_options,
            opt,
            _cmdln_canonical_path(
                cmdln_options.unix2win_path_mapping,
                getattr(cmdln_options, opt)))
        
        
def _cmdln_canonical_path(unix2win_path_mapping, unixpath):
    """Given a unix path return the platform-specific path
    
    On Windows, use the given mapping to translate the path. On Unix platforms,
    this function essentially returns `unixpath`.
    
    The mapping is simply a buildout.cfg-friendly multiline string that would
    get parsed as dictionary which should have path prefixes as keys, and the
    translated Windows net share path as the values. See PyPM's
    etc/activestate.conf for an example.
    
    The mapping is typically supposed to be defined in the config file under
    the cmdln section. This function is used by PyPM and Grail. 
    """
    unix2win_path_mapping = unix2win_path_mapping or ""
    
    # convert buildout.cfg-style multiline mapping to a dict
    m = dict([
        [x.strip() for x in line.strip().split(None, 1)]
        for line in unix2win_path_mapping.splitlines() if line.strip()])
    
    if sys.platform.startswith('win'):
        for prefix, netsharepath in m.items():
            if unixpath.startswith(prefix):
                return netsharepath + unixpath[len(prefix):]
    return unixpath