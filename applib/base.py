"""Base module"""

import sys
from os.path import abspath, join, expanduser

from applib import location


class Application(object):
    """Object representing the application
    
    - name:                   Name of the application
    
    - company:                Company developing the application
    
    - compatibility_version:  The major version which promises
                              backward-compatability among all of its minor
                              versions. Eg: 5.2; 5.2.1, 5.2.2, etc.. should
                              use the same compatability version (5.2). This
                              value is used in the settings directory path.
                              
    - locations:              An object holding a set of OS-specific but
                              generic location values (eg: APPDATA). See
                              ``Locations`` class for details.
    """

    def __init__(self, name, company, compatibility_version=None):
        self.name = name
        self.company = company
        self.compatibility_version = compatibility_version
        self.locations = Locations(self)

class Locations(object):
    """A object holding the locations that are generic to an application.
    
    The following locations are available:
    
    - user_data_dir:   Directory to store the user's settings
    - site_data_dir:   Directory to store global application settings
    - user_cache_dir:  Directory to keep temperory/cache files
    - log_file_path:   Location of the application log file
    """

    def __init__(self, app):
        self.app = app

    @property
    def user_data_dir(self):
        return location.user_data_dir(
            self.app.name, self.app.company, self.app.compatibility_version)

    @property
    def site_data_dir(self):
        return location.site_data_dir(
            self.app.name, self.app.company, self.app.compatibility_version)

    @property
    def user_cache_dir(self):
        return location.user_cache_dir(
            self.app.name, self.app.company, self.app.compatibility_version)
    
    @property
    def log_file_path(self):
        if sys.platform.startswith('win'):
            return join(self.user_cache_dir, self.app.name + '.log')
        elif sys.platform.startswith('darwin'):
            return join(expanduser('~/Library/Logs'), self.app.name + '.log')
        else:
            return join(expanduser('~'), self.app.name.lower() + '.log')

if __name__ == '__main__':
    # self-test code
    app = Application('PyPM', 'ActiveState', '0.1')
    print app.locations.user_data_dir
    print app.locations.site_data_dir
    print app.locations.user_cache_dir
    print app.locations.log_file_path

