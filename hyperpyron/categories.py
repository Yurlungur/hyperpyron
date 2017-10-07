#!/usr/bin/env python

"""
hyperpyron/categories.py
Author: Jonah Miller (jonah.maxwell.miller@gmail.com)
"""

# python
import yaml
import os
from os import path

# hyperpyron
from .sysdirs import cache_dir,conf_dir,parse_conf_dir

CATEGORIES = set(['Groceries',
                  'Restaurants',
                  'Healthcare',
                  'Retail',
                  'Automotive',
                  'Income',
                  'Cash',
                  'Entertainment',
                  'Transfer',
                  'Other'])
COLUMNS = ['Date','Description','Amount','Category']

categories_file=path.join(conf_dir,"categories.yaml")
default_categories = {
    'Automotive': [],
    'Cash': [],
    'Entertainment': [],
    'Groceries': [],
    'Healthcare': [],
    'Ignore': [],
    'Income': [],
    'Other' : [],
    'Restaurants': [],
    'Retail': [],
    'Transfer': []
}
def get_categories():
    "Load categories file, or try"
    try:
        categories = default_categories
        with open(categories_file,'r') as f:
            user_categories = yaml.load(f)
        for k in user_categories.keys():
            if k not in default_categories.keys():
                raise ValueError("Unknown category key: \n"
                                 +str(k))
            categories[k] += user_categories[k]
    except OSError:
        categories = default_categories
    return categories
