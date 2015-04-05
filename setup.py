#!/usr/bin/env python

import os
from setuptools import setup


setup(name='pymarkdown',
      version='0.1.0',
      description='Evaluate code in markdown',
      url='http://github.com/mrocklin/pymarkdown',
      author='Matthew Rocklin',
      author_email='mrocklin@gmail.com',
      license='BSD',
      keywords='markdown documentation',
      packages=['pymarkdown'],
      install_requires=[],
      long_description=(open('README.rst').read() if os.path.exists('README.rst')
                        else ''),
      zip_safe=False,
      scripts=[os.path.join('bin', 'pymarkdown')])
