#!/usr/bin/env python

"""
hyperpyron/vis.py
Author: Jonah Miller (jonah.maxwell.miller@gmail.com)
"""


import numpy as np
import pandas as pd
from datetime import date,timedelta,datetime
import matplotlib as mpl
from matplotlib import pyplot as plt


mpl.rcParams.update({'font.size': 16})



def filter_frame_between_dates(frame,before,after):
    """Filters a dataframe and selects for
    rows beween two dates, before
    and after.

    Dates assumed to be in
    YYYY-MM-DD
    format
    or standard datetime format
    """
    mask = (frame.Date >= before) & (frame.Date <= after)
    return frame.loc[mask]

def dataframe_from_n_days_ago_to_now(frame,n):
    """Returns a dataframe filtered to show
    dates between n days ago and now.
    """
    d = date.today() - timedelta(days=n)
    return filter_frame_between_dates(frame,
                                      d,date.today())

def ignore_income(frame):
    """Returns a dataframe ignoring income in frame"""
    mask = frame.Amount < 0
    out = frame.copy(deep=True)
    out = out.loc[mask]
    out.Amount *= -1.0
    return out

def calculate_percentages(frame):
    """Calculates the percentage expenditure in
    each category and returns a dataframe with this
    information.
    """
    out = ignore_income(frame)
    out = out.groupby('Category').apply(
        lambda x: x['Amount'].sum())
    tot = out.sum()
    out = 100*out/tot
    return out

def make_pie_chart(frame,
                   savepath=None,
                   show=True):
    """Takes a frame and makes a pie chart.
    Automatically calculates percentages.
    """
    toplot = calculate_percentages(frame)
    labels = toplot.index.tolist()
    vals = toplot.as_matrix()
    explode = 0.125*np.ones_like(vals)
    plt.pie(vals,labels=labels,
            radius = 1.5,
            shadow=True,
            explode=explode,
            startangle=90,
            autopct='%1.1f%%')
    if savepath:
        plt.savefig(savepath)
    if show:
        plt.show()
    return    

def get_category_sums(frame):
    """Sums up all categories
    and adds a total column
    """
    out = frame.groupby('Category').apply(
        lambda x:x['Amount'].sum())
    sum_df = pd.DataFrame([out.sum()],
                          index=["Total"])
    out = pd.concat([out,sum_df])
    out = out.rename(columns = {out.columns[0]:'Value'})
    out.columns.name = 'Category'
    return out

def compare_expenditures(frame,
                         savepath=None,
                         show=True):
    """Compares income and expenditures
    in bar chart
    """
    toplot = get_category_sums(frame)
    labels = toplot.index.tolist()
    vals = toplot.as_matrix().flatten()
    plt.bar(labels,vals,
            color='b',
            alpha = 0.8)
    plt.xticks(rotation=90)
    plt.ylabel('Net Change ($)')
    plt.xlabel('Category')
    if savepath:
        plt.savefig(savepath)
    if show:
        plt.show()
    return

