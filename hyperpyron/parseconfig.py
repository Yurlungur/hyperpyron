#!/usr/bin/env python

"""
hyperpyron/parseconfig.py
Author: Jonah Miller (jonah.maxwell.miller@gmail.com)
"""

# python
import yaml
import os
import re
import numpy as np
import pandas as pd
from abc import ABC,abstractmethod
from os import path

# hyperpyron
from . import iconfig
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

def invert_dict(my_map):
    "Invert a dictionary"
    return dict((v, k) for k, v in my_map.items())

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


class DataParser(ABC):
    """
    This is the base class for parsing and importing data.
    """
    def __init__(self,data_rules):
        self.categories = get_categories()
        data_rules = self.validate_rules(data_rules)
        self.file_names = []
        self.rules = data_rules
        self.frame = self.import_all()

    def import_all(self):
        rules = self.rules
        frames = []
        for root,dirs,files in os.walk(rules['directory']):
            for name in files:
                fpath = path.join(root,name)
                self.file_names.append(fpath)
                if iconfig.DEBUG:
                    print("Reading in: ",name)
                frames.append(self.import_one(fpath))
        if not frames:
            return None
        frame = pd.concat(frames)
        if 'duplicate checking' in rules.keys():
            if rules['duplicate checking']:
                frame = self.remove_duplicates(frame)
        frame = self.standardize_columns(frame)
        frame = self.standardize_categories(frame)
        frame = self.categorize_missing(frame)
        frame = self.drop_rows(frame)
        return frame

    def get_frame(self):
        return self.frame

    def drop_rows(self,frame):
        "Ignore a row if the categories file tells us to"
        out = frame.copy()
        for c in self.categories['Ignore']:
            out = out[out.Category != c]
        return out

    def categorize_missing(self,frame):
        """The categories file tells us how to
        categorize some transactions based on
        their description. We utilize that here.
        """
        out = frame.copy()
        for c in CATEGORIES:
            for d in self.categories[c]:
                row_mask = out["Description"].apply(
                    lambda x: d in x.lower())
                out.loc[row_mask,"Category"] = c
        row_mask = out["Category"].apply(
            lambda x: x not in CATEGORIES)
        out.loc[row_mask,"Category"] = "Other"
        return out

    @abstractmethod
    def import_one(self,fpath):
        "Import one file and return it"

    @abstractmethod
    def remove_duplicates(self,frame):
        "Remove duplicates from frame if possible"

    @abstractmethod
    def standardize_columns(self,frame):
        "Make column names standard and return them."

    @abstractmethod
    def standardize_categories(self,frame):
        "Make sure spending categories are consistent"

    @abstractmethod
    def validate_rules(self,data_rules):
        "Makes sure data rules are consistent"

class CSVParser(DataParser):
    """The data parser for CSV files.
    """
    def validate_rules(self,data_rules):
        if data_rules['type'] != 'csv':
            raise ValueError("CSVParser only works for CSV files")
        if 'skip lines' not in data_rules.keys():
            data_rules['skip lines'] = 0
        if type(data_rules['skip lines']) is not int:
            raise TypeError("Must skip integer number of lines")
        if data_rules['skip lines'] < 0:
            raise TypeError("Must skip positive number of lines")
        if set(data_rules['columns'].keys()) != set(COLUMNS):
            raise ValueError("The columns must be exactly:\n"
                             +"\tDate\n"
                             +"\tDescription\n"
                             +"\tAmount\n"
                             +"\tCategory\n"
                             +"in any order.")
        if 'duplicate checking' not in data_rules.keys():
            data_rules['duplicate checking'] = False
        if data_rules['duplicate checking']:
            if 'hash column' not in data_rules.keys():
                raise ValueError("If you use duplicate checking,"
                                 +" you must include a"
                                 +" hash column.")
        if 'expenditures positive' not in data_rules.keys():
            data_rules['expenditures positive'] = False
        if type(data_rules['expenditures positive']) is not bool:
                raise TypeError("'expenditures positive'"
                                " must be a Boolean.")
        return data_rules

    def import_one(self,fpath):
        rules = self.rules
        if rules['use column names']:
            usecols = list(rules['columns'].values())
            if rules['duplicate checking']:
                usecols.append(rules['hash column'])
        else:
            usecols = sorted(rules['columns'].values())
            if rules['duplicate checking']:
                usecols = sorted(usecols
                                 + [rules['hash column']])
        df = pd.read_csv(fpath,usecols=usecols)
        return df

    def standardize_columns(self,frame):
        rules = self.rules
        name_map = invert_dict(rules['columns'])
        if rules['use column names']:
            out = frame.rename(columns = name_map)
        else:
            name_map = dict((frame.columns[k],v)\
                            for k,v in name_map.items())
            out = frame.rename(columns = name_map)
        if not np.any(out["Amount"].apply(
                lambda x: type(x) is float)):
            out["Amount"] = out["Amount"].apply(
                lambda x: float(x.lstrip("$")))
        if rules['expenditures positive']:
            out["Amount"] = out["Amount"].apply(
                lambda x: x*-1)
        return out

    def standardize_categories(self,frame):
        out = frame.copy()
        for k,v in self.rules['categories'].items():
            out.loc[out.Category==k,"Category"]=v
        return out

    def remove_duplicates(self,frame):
        rules = self.rules
        if rules['use column names']:
            c = rules['hash column']
        else:
            c = frame.columns[rules['hash column']]
        out = frame.drop_duplicates(subset=c,
                                    keep='first')
        del out[rules['hash column']]
        return out

