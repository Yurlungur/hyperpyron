#!/usr/bin/env python

"""
hyperpyron/budget.py
Author: Jonah Miller (jonah.maxwell.miller@gmail.com)
"""

# python
import yaml
import os
import numpy as np
import pandas as pd
from os import path

# hyperpyron
from .sysdirs import conf_dir
from .categories import CATEGORIES,get_categories

default_budget = {c : 0 for c in CATEGORIES}
budget_file = path.join(conf_dir,"budget.yaml")

def get_budget():
    "Load budget file, or try"
    budget = default_budget
    categories = get_categories()
    try:
        with open(budget_file,'r') as f:
            user_budget = yaml.load(f)
    except OSError:
        budget = default_budget
    else:
        for category,contributions in user_budget.items():
            if type(contributions) is dict:
                contributions = list(contributions.values())
            total = np.sum(contributions)
            if category in CATEGORIES:
                budget[category] += total
            else:
                budget["Other"] += total
    for cat,cost in budget.items():
        budget[cat] = -np.abs(cost)
    budget["Income"] = np.abs(budget["Income"])
    total = np.sum(list(budget.values()))
    budget["Total"] = total
    for c in categories['Ignore']:
        if c in budget.keys():
            del budget[c]
    budget = pd.Series(budget,name="Budget")
    return budget
