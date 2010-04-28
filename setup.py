
# http://bitbucket.org/srid/modern-package-template/issue/9/distribute_setup-should-not-be-used#comment-139503
# import distribute_setup
# distribute_setup.use_setuptools()

from setuptools import setup, find_packages
import sys, os
from os import path


here = os.path.abspath(path.dirname(__file__))
README = open(path.join(here, 'README.txt')).read()
NEWS = open(path.join(here, 'NEWS.txt')).read()

# make sure that we import applib/ (and not the system-wide one)
sys.path.insert(0, path.abspath(path.dirname(__file__)))
import applib


setup(name='applib',
      version=applib.__version__,
      description="Cross-platform application utilities",
      long_description=README + '\n\n' + NEWS,
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Utilities',
      ],
      keywords='',
      author='Sridhar Ratnakumar',
      author_email='srid@nearfar.org',
      url='http://bitbucket.org/srid/applib',
      license='MIT',
      packages=find_packages(exclude=[
          'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
