#!/usr/bin/env python

"""
hyperpyron/__init__.py
Author: Jonah Miller (jonah.maxwell.miller@gmail.com)
"""

# Python
import os
import errno

# Hyperpyron
from . import iconfig
from ._version import __version__
from .sysdirs import cache_dir,conf_dir,parse_conf_dir
from .analysis import *
from .hyperparse import *

def make_sure_path_exists(path):
    "Make the path, if it doesn't already exist"
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

# Check directories and make them if necessary
make_sure_path_exists(cache_dir)
make_sure_path_exists(conf_dir)
make_sure_path_exists(parse_conf_dir)

