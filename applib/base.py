"""Base module"""

from applib import location


class Application(object):

    def __init__(self, name, company, compatibility_version=None):
        self.name = name
        self.company = name
        self.compatibility_version = compatibility_version
        self.locations = Locations(self)

class Locations(object):

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
    

if __name__ == '__main__':
    # self-test code
    app = Application('PyPM', 'ActiveState', '1')
    print app.locations.user_data_dir
    print app.locations.site_data_dir
    print app.locations.user_cache_dir

