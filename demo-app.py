# Demonstration of `applib` features

import logging

from applib.base import Cmdln, Application
from applib.misc import require_option
from applib import textui, sh, _cmdln as cmdln

LOG = logging.getLogger(__name__)

application = Application('demo-app', 'CompanyNameHere', '1.2')


@cmdln.option('', '--foo', action='store_true', help='*must pass --foo')
class Commands(Cmdln):
    name = "demo-app"

    def initialize(self):
        require_option(self.options, 'foo')

    @cmdln.alias('cd')
    @cmdln.option('-t', '--show-time', action='store_true',
                  help='Also show the current time')
    def do_currentdate(self, subcmd, opts):
        """${cmd_name}: Show the current date
        
        ${cmd_usage}
        ${cmd_option_list}
        """
        with self.bootstrapped():
            from datetime import datetime
            now = datetime.now()
            LOG.debug('datetime.now = %s', now)
            if opts.show_time:
                print(now)
            else:
                print(now.date())
                
    def do_ls(self, subcmd, opts):
        """${cmd_name}: Show directory listing (runs 'ls')
        
        ${cmd_usage}
        ${cmd_option_list}
        """
        with self.bootstrapped():
            print(sh.run('ls')[0].decode('utf-8'))
                
    def do_makeerror(self, subcmd, opts, what):
        """${cmd_name}: Make an error. Use -v to see full traceback
        
        ${cmd_usage}
        ${cmd_option_list}
        """
        with self.bootstrapped():
            LOG.debug('About to make an error! %s', what)
            textui.askyesno('Press enter to proceed:', default=True)
            1/0
            
    def do_think(self, subcmd, opts, length=200):
        """${cmd_name}: Progress bar example
        
        ${cmd_usage}
        ${cmd_option_list}
        """
        with self.bootstrapped():
            import time
            length = int(length)
            for x in textui.ProgressBar.iterate(range(length)):
                if x == length-1:
                    break # test that break doesn't mess up output
                time.sleep(0.1)
            
    def do_multable(self, subcmd, opts, number=10, times=25):
        """${cmd_name}: Print multiplication table
        
        To demonstrate `colprint` feature
        
        ${cmd_usage}
        ${cmd_option_list}
        """
        with self.bootstrapped():
            textui.colprint([
                [str(x*y) for y in range(1, 1+int(times))]
                for x in range(1, 1+int(number))
            ])


if __name__ == '__main__':
    application.run(Commands)

