# Demonstration of `applib` features

import logging

from applib.base import Cmdln, Application
from applib.misc import require_option
from applib import textui, _cmdln as cmdln

LOG = logging.getLogger(__name__)

application = Application('demo-app', 'CompanyNameHere', '1.0.1')


@cmdln.option('', '--dummy', action='store_true')
class Commands(Cmdln):
    name = "demo-app"

    def initialize(self):
        require_option(self.options, 'dummy')

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
                print now
            else:
                print now.date()
                
    def do_makeerror(self, subcmd, opts):
        """${cmd_name}: Make an error. Use -v to see full traceback
        
        ${cmd_usage}
        ${cmd_option_list}
        """
        with self.bootstrapped():
            LOG.debug('About to make an error!')
            1/0
            
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

