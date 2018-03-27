#!/usr/bin/env python

from setuptools import find_packages, setup

setup(name='carriage',
      version='0.1dev',
      description='Enhanced collection classes for programming fluently',
      author='Yen, Tzu-Hsi',
      author_email='joseph.yen@gmail.com',
      url='https://github.com/d2207197/carriage',
      packages=find_packages(),
      classifiers=[
          # How mature is this project? Common values are
          #   3 - Alpha
          #   4 - Beta
          #   5 - Production/Stable
          'Development Status :: 3 - Alpha',

          # Indicate who your project is intended for
          'Intended Audience :: Developers',
          'Software Development :: Libraries :: Python Modules'


          # Pick your license as you wish (should match "license" above)
          'License :: OSI Approved :: MIT License',

          # Specify the Python versions you support here. In particular, ensure
          # that you indicate whether you support Python 2, Python 3 or both.
          'Programming Language :: Python :: 3.6',
      ],

      )
