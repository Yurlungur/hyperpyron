#!/usr/bin/env python

"""setup.py
Author: Jonah Miller (jonah.maxwell.miller@gmail.com)
Time-stamp: <2017-10-08 14:55:26 (jmiller)>

This is the setup.py file for the hyperpyron package
which is an finance and budgeting tool with transparent,
plaintext configurable automation.
"""

from setuptools import setup,find_packages

exec(open('hyperpyron/_version.py','r').read())
with open('README.md','r') as f:
    long_description = f.read()

setup(
    name='hyperpyron',
    version=__version__,
    description='a transparent, plaintext configurable budgeting tool',
    long_description=long_description,
    url='https://github.com/Yurlungur/hyperpyron',
    author = 'Jonah Miller',
    author_email = 'jonah.maxwell.miller@gmail.com',
    license = 'GPLv3',
    classifiers = [
        'Development status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'Environment :: Console',
        'License :: General Public License v3',
        'Natural Language :: English',
        'Operating System :: Unix',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
    keywords = 'simulations relativity science computing',
    packages = find_packages(),
    install_requires = ['numpy',
                        'scipy',
                        'matplotlib',
                        'pandas',
                        'appdirs']
)
