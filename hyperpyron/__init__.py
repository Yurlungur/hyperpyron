#!/usr/bin/env python

"""
hyperpyron/__init__.py
Author: Jonah Miller (jonah.maxwell.miller@gmail.com)
"""

# Python
import os
import errno
from appdirs import AppDirs

# Hyperpyron
from . import iconfig
from ._version import __version__

def make_sure_path_exists(path):
    "Make the path, if it doesn't already exist"
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

# Check directories and make them if necessary
hyperpyron_home = os.environ.get('HYPERPYRON_HOME')
if hyperpyron_home is not None:
    cache_dir = hyperpyron_home + "/" + iconfig.CACHE_DIR
    conf_dir = hyperpyron_home + "/" + iconfig.CONF_DIR
else:
    dirs = AppDirs(iconfig.APP_NAME,iconfig.APP_AUTHOR)
    cache_dir = dirs.user_cache_dir
    conf_dir = dirs.user_data_dir
if iconfig.DEBUG:
    print("Data and home directories:")
    print("\t",cache_dir)
    print("\t".conf_dir)
make_sure_path_exists(cache_dir)
make_sure_path_exists(conf_dir)


