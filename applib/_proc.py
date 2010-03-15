"""Process execution wrappers
"""

import os
import sys
import time
import subprocess
from tempfile import TemporaryFile
from contextlib import nested

from applib.misc import xjoin

__all__ = ['run', 'RunError', 'RunNonZeroReturn', 'RunTimedout']


class RunError(Exception): pass


class RunNonZeroReturn(RunError):
    """The command returned non-zero exit code"""

    def __init__(self, p, cmd, stdout, stderr):
        self.stdout = stdout
        self.stderr = stderr
        
        msg = '\n'.join([
            'non-zero returncode: {0}'.format(p.returncode),
            'command: {0}'.format(cmd),
            'pwd: {0}'.format(xjoin(os.getcwd())),
            'stderr:\n{0}'.format(stderr),
            'stdout:\n{0}'.format(stdout),
            ])
        super(RunNonZeroReturn, self).__init__(msg)


class RunTimedout(RunError):
    """process is taking too much time"""

    def __init__(self, cmd, timeout, stdout, stderr):
        msg = '\n'.join([
            'timed out; ergo process is terminated',
            'seconds elapsed: {0}'.format(timeout),
            'command: {0}'.format(cmd),
            'pwd: {0}'.format(xjoin(os.getcwd())),
            'stderr:\n{0}'.format(stderr),
            'stdout:\n{0}'.format(stdout),
            ])
        super(TimeoutError, self).__init__(msg)

    
# TODO: support for incremental results (sometimes a process run for a few
# minutes, but we need to send the stdout as soon as it appears.
def run(cmd, merge_streams=False, timeout=None, env=None):
    """Improved replacement for commands.getoutput()

    The following features are implemented:

     - timeout (in seconds)
     - support for merged streams (stdout+stderr together)

    Note that returned data is of *undecoded* str/bytes type (not unicode)

    Return (stdout, stderr)
    """
    # Fix for cmd.exe quote issue. See comment #3 and #4 in
    # http://firefly.activestate.com/sridharr/pypm/ticket/126#comment:3
    if sys.platform.startswith('win') and cmd.startswith('"'):
        cmd = '"{0}"'.format(cmd)

    # redirect stdout and stderr to temporary *files*
    with nested(TemporaryFile(), TemporaryFile()) as (outf, errf):
        p = subprocess.Popen(cmd, env=env, shell=True, stdout=outf,
                             stderr=outf if merge_streams else errf)

        if timeout is None:
            p.wait()
        else:
            # poll for terminated status till timeout is reached
            t_nought = time.time()
            seconds_passed = 0
            while True:
                if p.poll() is not None:
                    break
                seconds_passed = time.time() - t_nought
                if timeout and seconds_passed > timeout:
                    p.terminate()
                    raise RunTimedout(
                        cmd, timeout,
                        _read_tmpfd(outf), _read_tmpfd(errf))
                time.sleep(0.1)

        # the process has exited by now; nothing will to be written to
        # outfd/errfd anymore.
        stdout = _read_tmpfd(outf)
        stderr = _read_tmpfd(errf)

    if p.returncode != 0:
        raise RunNonZeroReturn(p, cmd, stdout, stderr)
    else:
        return stdout, stderr


def _read_tmpfd(fil):
    """Read from a temporary file object

    Call this method only when nothing more will be written to the temporary
    file - i.e., all the writing has already been done.
    """
    fil.seek(0)
    return fil.read()


def _disable_windows_error_popup():
    """Set error mode to disable Windows error popup
    
    This setting is effective for current process and all the child processes
    """
    # disable nasty critical error pop-ups on Windows
    import win32api, win32con
    win32api.SetErrorMode(win32con.SEM_FAILCRITICALERRORS |
                          win32con.SEM_NOOPENFILEERRORBOX)
if sys.platform.startswith('win'):
    try:
        import win32api
    except ImportError:
        pass # XXX: this means, you will get annoying popups
    else:
        _disable_windows_error_popup()
