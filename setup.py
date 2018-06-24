#!/usr/bin/env python

import itertools as itt

from setuptools import find_packages, setup

extras_require = {'pandas': ['pandas']}
extras_require['all'] = set(itt.chain.from_iterable(extras_require.values()))

setup(name='carriage',
      version='0.4.3',
      description='Enhanced collection classes for programming fluently',
      author='Yen, Tzu-Hsi',
      author_email='joseph.yen@gmail.com',
      url='https://github.com/d2207197/carriage',
      packages=find_packages(),
      install_requires=['tabulate'],
      extras_require=extras_require,
      classifiers=[
          # How mature is this project? Common values are
          #   3 - Alpha
          #   4 - Beta
          #   5 - Production/Stable
          'Development Status :: 4 - Beta',

          # Indicate who your project is intended for
          'Intended Audience :: Developers',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Operating System :: OS Independent',

          # Pick your license as you wish (should match "license" above)
          'License :: OSI Approved :: MIT License',

          # Specify the Python versions you support here. In particular, ensure
          # that you indicate whether you support Python 2, Python 3 or both.
          'Programming Language :: Python :: 3.6',
      ],

      )
