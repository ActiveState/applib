from setuptools import setup, find_packages
import sys, os
from os import path


here = os.path.abspath(path.dirname(__file__))
README = open(path.join(here, 'README.rst')).read()
NEWS = open(path.join(here, 'NEWS.txt')).read()

# make sure that we import applib/ (and not the system-wide one)
sys.path.insert(0, path.abspath(path.dirname(__file__)))
import applib


setup(name='applib',
      version=applib.__version__,
      description="Cross-platform application utilities in Python",
      long_description=README + '\n\n' + NEWS,
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2.6', # minimum supported = 2.6
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Utilities',
      ],
      keywords='',
      author='Sridhar Ratnakumar',
      author_email='github@srid.name',
      url='http://github.com/ActiveState/applib',
      license='MIT',
      packages=find_packages(exclude=[
          'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'appdirs', 'six',
      ],
      )
