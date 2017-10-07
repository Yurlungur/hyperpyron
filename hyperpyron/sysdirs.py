#!/usr/bin/env python

"""
hyperpyron/sysdirs.py
Author: Jonah Miller (jonah.maxwell.miller@gmail.com)
"""

# python
import os
from os import path
from appdirs import AppDirs

# hyperpyron
from . import iconfig

def get_sysdirs():
    hyperpyron_home = os.environ.get('HYPERPYRON_HOME')
    if hyperpyron_home:
        if iconfig.DEBUG:
            print("hyerpyron_home = ",hyperpyron_home)
        cache_dir =path.join(hyperpyron_home,iconfig.CACHE_DIR)
        conf_dir = path.join(hyperpyron_home,iconfig.CONF_DIR)
    else:
        dirs = AppDirs(iconfig.APP_NAME,iconfig.APP_AUTHOR)
        cache_dir = dirs.user_cache_dir
        conf_dir = dirs.user_data_dir
    parse_conf_dir = path.join(conf_dir,iconfig.PARSECONF_DIR)
    if iconfig.DEBUG:
        print("Data and home directories:")
        print("\t",cache_dir)
        print("\t",conf_dir)
        print("\t",parse_conf_dir)
    return cache_dir,conf_dir,parse_conf_dir

cache_dir,conf_dir,parse_conf_dir = get_sysdirs()
