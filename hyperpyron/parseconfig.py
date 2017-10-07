#!/usr/bin/env python

"""
hyperpyron/parseconfig.py
Author: Jonah Miller (jonah.maxwell.miller@gmail.com)
"""

# python
import yaml
import os
from abc import ABC,abstractmethod
from os import path

# hyperpyron
from . import iconfig
from .sysdirs import cache_dir,conf_dir,parse_conf_dir
from .utils import invert_dict
from .categories import CATEGORIES,COLUMNS,get_categories

class DataRulesParser:
    """
    This class parses the rules for importing data
    from various classes. The parser caches
    information, so the data can be recalled.

    Initiate with
    p = DataRulesParser(parse_conf_dir)
    """
    def __init__(self,parse_conf_dir):
        self.parsed_rules = {}
        self.parse_directory(parse_conf_dir)

    def parse_one_file(self,fname):
        with open(fname,'r') as f:
            self.parsed_rules[fname] = yaml.load(f.read())
        return self.parsed_rules[fname]

    def parse_directory(self,d):
        for root, dirs, files in os.walk(d):
            for name in files:
                fpath = path.join(root,name)
                if iconfig.DEBUG:
                    print("parsing ",fpath)
                self.parse_one_file(fpath)
        return self.parsed_rules

    def keys(self):
        return self.parsed_rules.keys()

    def values(self):
        return self.parsed_rules.values()

    def reset(self):
        self.parsed_rules = {}

    def __getitem__(self,a):
        return self.parsed_rules[a]

    def __len__(self):
        return len(self.parsed_rules)

