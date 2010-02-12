import distribute_setup
distribute_setup.use_setuptools()

from setuptools import setup, find_packages
import sys, os
from os import path


if sys.version_info[:2] >= (3, 0):
    raise SystemExit, 'applib is not ported to Python 3 yet.'

# make sure that we import applib/ (and not the system-wide one)
sys.path.insert(0, path.abspath(path.dirname(__file__)))
import applib


setup(name='applib',
      version=applib.__version__,
      description="Cross-platform application utilities",
      long_description="""\
""",
      classifiers=[
          'Development Status :: 3 - Alpha',
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
          'distribute_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
