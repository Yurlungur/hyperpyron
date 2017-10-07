#!/usr/bin/env python

"""
hyperpyron/hyperparse.py
Author: Jonah Miller (jonah.maxwell.miller@gmail.com)
"""

# python
from os import path
import numpy as np
import pandas as pd

# hyperpyron
from . import iconfig
from .sysdirs import cache_dir,conf_dir,parse_conf_dir
from .utils import invert_dict
from .categories import CATEGORIES,COLUMNS,get_categories
from .parsers import parsers
from .parseconfig import DataRulesParser

def parse_from_data():
    "Loads data from files specified in YAML configs"
    all_rules = DataRulesParser(parse_conf_dir)
    frames = []
    for rules in all_rules.values():
        ParserClass = parsers[rules['type']]
        p = ParserClass(rules)
        frames.append(p.get_frame())
    frame = pd.concat(frames,
                      axis=0,
                      ignore_index=True)
    frame.reset_index(inplace=True)
    return frame

def save_to_cache(frame):
    "Save a data frame to the cache"
    frame.to_hdf(path.join(cache_dir,
                           iconfig.FCACHE_NAME),
                 'df')

def load_from_cache():
    "Load a data frame from cache"
    target = path.join(cache_dir,
                       iconfig.FCACHE_NAME)
    try:
        frame = pd.read_hdf(target,'df')
    except FileNotFoundError:
        frame = None
    return frame
