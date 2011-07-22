#!/usr/bin/env python

import os
from distutils.core import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(name='Deft',
      version='0.2.0',
      description='Easy Distributed Feature Tracking',
      long_description=read("README.rst"),
      author='Nat Pryce',
      author_email='about-deft@natpryce.com',
      url='http://github.com/npryce/deft',
      
      license="GPL3",
      
      classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Topic :: Software Development :: Bug Tracking',
        'Topic :: Utilities'],
      platforms=['any'],
      
      provides=['deft'],
      packages=['deft', 'deft.storage', 'deft.history', 'deft.systests'],
      package_dir = {'': 'src'},
      scripts=['bin/deft', 'bin/deft-cfd'],
      
      requires=[
        'yaml (==3.10)', 
        'argparse (==1.2)', 
        'functional (==0.4)',
        'dulwich (==0.7.1)'],
      
      test_requires=[
        'nose (1.0.0)',
        'hamcrest (1.5)'],
      test_suite='nose.collector')
