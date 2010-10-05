"""Textual UI: progress bar and colprint"""

import sys
from datetime import datetime, timedelta
from contextlib import contextmanager
import logging
import math

import six

LOG = logging.getLogger(__name__)

__all__ = ['colprint', 'find_console_width', 'ProgressBar',
           'clear_progress_bar', 'redraw_progress_bar', 'safe_output']

if not six.PY3:
    input = raw_input


class ProgressBar(object):
    """Show percent progress every 'n' seconds"""

    def __init__(self, total, delay=0.1, show_size=lambda x: x, note=None):
        """
        total - total number of items that are going to be processed
        delay - update delay in seconds
        show_size - function to return the string to display instead of the number `size`
        """
        assert total >= 0, total
        assert delay >= 0, delay
        assert show_size
        
        _set_current_progress_bar(self)
        self.delay = timedelta(seconds=delay)
        self.start = datetime.now()
        self.estimated_time_left = None
        self.lastprint = None
        self.lastprocessed = 0
        self.total = total
        self.processed = 0
        self.show_size = show_size
        self.note = note
        self._length = 0 # current length of the progress display

    @classmethod
    def iterate(cls, sequence, note=None):
        """Iterate a sequence and update the progress accordingly

        The sequence must have a 'len' attribute and thus not expected to be a
        generator/iterator.
        """
        p = cls(len(sequence), note=note)
        for item in sequence:
            yield item
            p.tick()
        p.close()

    def tick(self, items=1):
        """The method that updates the display if necessary.

        After creating the ``PercentProgress`` object, this method must be
        called for every item processed (or, pass items=ITEMS for every ITEMS
        processed).

        This method must be called no more than ``self.total`` times (otherwise
        you get assertion error .. implying a bug in your code)

        Return True if progress bar was redrawn.
        """
        self.processed += items
        assert self.processed <= self.total, \
            '{0} <= {1}'.format(self.processed, self.total)
        
        now = datetime.now()
        if (self.lastprint == None or
            (now - self.lastprint) > self.delay):
            self.lastprint = now
            self.redraw()
            return True
        else:
            return False

    def clear(self):
        """Erase the entire progress bar and put the cursor at first column"""
        # Move cursor to the beginning of current progress line so that further
        # messages will overwrite the progress bar. Also overwrite the previous
        # progress bar with empty space.
        sys.stdout.write('\r' + ' '*self._length + '\r')
        sys.stdout.flush()

    def close(self):
        """Close (hide) the progress bar

        Erase the progress bar and print the closing message in place of the
        previous progress bar text.
        """
        self.redraw()
        self.clear()
        _del_current_progress_bar(self)

    def redraw(self):
        self.clear()
        percent = _calculate_percent(self.processed, self.total)
        now = datetime.now()
        delta = now - self.start
        self.estimated_time_left = delta.seconds * (100.0-percent)/percent

        bar_width = 20
        bar_filled = int(round(20.0/100 * percent))
        filled = ['+'] * bar_filled
        if filled:
            filled[-1] = '>'
        filled = ''.join(filled)
            
        progress_bar = ''.join([
            (self.note+': ') if self.note else '',
            # header:
            '[',

            # solid bar
            filled,

            # empty space
            ' ' * (bar_width-bar_filled),

            # footer
            '] {0:-3}% {1}/{2} ({3}; ETA:{4})'.format(
                percent,
                self.show_size(self.processed),
                self.show_size(self.total),
                _format_duration(delta.seconds),
                _format_duration(self.estimated_time_left),
            )
        ])
        
        self._length = len(progress_bar)
        sys.stdout.write('\r' + progress_bar + '\r')
        sys.stdout.flush()


def clear_progress_bar():
    """Clear progress bar, if any"""
    if _current_progress_bar:
        _current_progress_bar.clear()


def redraw_progress_bar():
    """Redraw progress bar, if any"""
    if _current_progress_bar:
        _current_progress_bar.redraw()


@contextmanager
def safe_output():
    """Wrapper that makes it safe to print to stdout

    If a progress bar is currently being shown, this wrapper takes care of
    clearing it before .. and then redrawing it after
    """
    clear_progress_bar()
    yield
    redraw_progress_bar()
    
    
def askyesno(question, default):
    """Ask (Y/N) type of question to the user"""
    assert isinstance(default, bool), '"default" must be a boolean'
    
    s = '{0} ({1}/{2}) '.format(
        question,
        default and 'Y' or 'y',
        default and 'n' or 'N')

    while True:
        val = input(s).strip().lower()
        
        if val == '':
            return default
        elif val in ('y', 'yes', 'ok'):
            return True
        elif val in ('n', 'no'):
            return False


# This function was written by Alex Martelli
# http://stackoverflow.com/questions/1396820/
def colprint(table, totwidth=None):
    """Print the table in terminal taking care of wrapping/alignment

    - `table`:    A table of strings. Elements must not be `None`
    - `totwidth`: If None, console width is used
    """
    if not table: return
    if totwidth is None:
        totwidth = find_console_width()
        totwidth -= 1 # for not printing an extra empty line on windows
    numcols = max(len(row) for row in table)
    # ensure all rows have >= numcols columns, maybe empty
    padded = [row+numcols*['',] for row in table]
    # compute col widths, including separating space (except for last one)
    widths = [ 1 + max(len(x) for x in column) for column in zip(*padded)]
    widths[-1] -= 1
    # drop or truncate columns from the right in order to fit
    while sum(widths) > totwidth:
        mustlose = sum(widths) - totwidth
        if widths[-1] <= mustlose:
            del widths[-1]
        else:
            widths[-1] -= mustlose
            break
    # and finally, the output phase!
    for row in padded:
        s = ''.join(['%*s' % (-w, i[:w])
                     for w, i in zip(widths, row)])
        LOG.info(s)


def find_console_width():
    if sys.platform.startswith('win'):
        return _find_windows_console_width()
    else:
        return _find_unix_console_width()


@contextmanager
def longrun(log, finalfn=lambda: None):
    """Decorator for performing a long operation with consideration for the
    command line.

    1. Catch keyboard interrupts and exit gracefully

    2. Print total time elapsed always at the end (successful or not)

    3. Call ``finalfn`` always at the end (successful or not)
    """
    start_time = datetime.now()

    try:
        yield
    except KeyboardInterrupt:
        log.info('*** interrupted by user - Ctrl+c ***')
        raise SystemExit(3)
    finally:
        finalfn()
        end_time = datetime.now()

        log.info('')
        log.info('-----')
        log.info('Total time elapsed: %s', end_time-start_time)
        
        
def _find_unix_console_width():
    """Return the width of the Unix terminal

    If `stdout` is not a real terminal, return the default value (80)
    """
    import termios, fcntl, struct, sys

    # fcntl.ioctl will fail if stdout is not a tty
    if not sys.stdout.isatty():
        return 80

    s = struct.pack("HHHH", 0, 0, 0, 0)
    fd_stdout = sys.stdout.fileno()
    size = fcntl.ioctl(fd_stdout, termios.TIOCGWINSZ, s)
    height, width = struct.unpack("HHHH", size)[:2]
    return width


def _find_windows_console_width():
    """Return the width of the Windows console

    If the width cannot be determined, return the default value (80)
    """
    # http://code.activestate.com/recipes/440694/
    from ctypes import windll, create_string_buffer
    STDIN, STDOUT, STDERR = -10, -11, -12
    
    h = windll.kernel32.GetStdHandle(STDERR)
    csbi = create_string_buffer(22)
    res = windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)

    if res:
        import struct
        (bufx, bufy, curx, cury, wattr,
         left, top, right, bottom,
         maxx, maxy) = struct.unpack("hhhhHhhhhhh", csbi.raw)
        sizex = right - left + 1
        sizey = bottom - top + 1
    else:
        sizex, sizey = 80, 25

    return sizex



def _byteshr(bytes):
    """Human-readable version of bytes count"""
    for x in ['bytes','KB','MB','GB','TB']:
        if bytes < 1024.0:
            return "%3.1f%s" % (bytes, x)
        bytes /= 1024.0
    raise ValueError('cannot find human-readable version')


def _calculate_percent(numerator, denominator):
    assert numerator <= denominator, '%d <= %d' % (numerator, denominator)
    if denominator == 0:
        if numerator == 0:
            return 100
        else:
            raise ValueError('denominator cannot be zero')

    return int(round( numerator / float(denominator) * 100 ))
    

def _format_duration(seconds):
    s = []
    if seconds > 60:
        s.append('{0}m'.format(int(seconds/60)))
    s.append('{0}s'.format(int(seconds % 60)))
    return ''.join(s)


# Handle to the current progress bar object.  There cannot be more than one
# progress bar for obvious reasons.
_current_progress_bar = None
def _set_current_progress_bar(pbar):
    global _current_progress_bar
    assert _current_progress_bar is None, 'there is already a pbar'
    _current_progress_bar = pbar
def _del_current_progress_bar(pbar):
    global _current_progress_bar
    assert _current_progress_bar is pbar, 'pbar is something else'
    _current_progress_bar = None

