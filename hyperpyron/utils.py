#!/usr/bin/env python

"""
hyperpyron/utils.py
Author: Jonah Miller (jonah.maxwell.miller@gmail.com)
"""

def invert_dict(my_map):
    "Invert a dictionary"
    return dict((v, k) for k, v in my_map.items())
