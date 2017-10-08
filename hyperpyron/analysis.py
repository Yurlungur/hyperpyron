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

def combine_percentages(frame,cutoff):
    """Combines percentages for a frame showing
    percentages for a frame. All percentages less
    than cutoff get placed into the "other" category.

    IMPORTANT: assumes frame has already
    passed through "analysis.calculate_percentages.
    """
    if cutoff <= 0:
        return frame
    if cutoff >= 100:
        raise ValueError("Can't cutoff more than 100%"
                         " of expenditures!")
    remaining = frame.loc[frame >= cutoff]
    consolidated = frame.loc[frame < cutoff]
    if "Other" in remaining.index.tolist():
        remaining = remaining.copy(deep=True)
        remaining["Other"] += consolidated.sum()
        return remaining
    sum_df = pd.DataFrame([consolidated.sum()],
                          index=["Other"])
    out = pd.concat([remaining,sum_df])
    out = out.rename(columns = {out.columns[0]:'Value'})
    out.columns.name = 'Category'
    return out

def plot_percent_expenditures(frame,
                              savepath=None,
                              show=True,
                              cutoff = 0.0):
    """Takes a frame and makes a pie chart.
    Automatically calculates percentages.

    Pie chart should automatically align to
    be legible.
    """
    toplot = calculate_percentages(frame)
    toplot = combine_percentages(toplot,cutoff)
    toplot = toplot.sort_values(ascending=False)
    labels = toplot.index.tolist()
    vals = toplot.as_matrix()
    num_categories = len(vals)
    transition_num = 4
    calibration_categories = 9
    e_calibration = 1.2
    emax_base = e_calibration/calibration_categories
    emin = 0.075
    if num_categories > transition_num:
        x = np.linspace(0,1,num_categories)
        emax = emax_base * num_categories
        explode = emin+emax*x*x
    else:
        explode = emin*np.ones_like(vals)
    plt.pie(vals,labels=labels,
            radius = 1.2,
            shadow=True,
            explode=explode,
            startangle=90,
            pctdistance=0.8,
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

def combine_expenses(frame,cutoff):
    """Calculates net category sums as above,
    but if the percentages of the total are less than
    cutoff, consolidates them into the "Other" category.
    """
    if len(frame.shape) > 1 and frame.shape[1] > 1:
        sums = get_category_sums(frame)
    else:
        sums = frame
    if cutoff <= 0:
        return sums
    if cutoff >= 100:
        raise ValueError("Can't cutoff more than 100%"
                         " of expenditures!")
    positive = np.abs(sums)
    positive.loc["Total"] = positive.drop("Total").sum()
    percentages = 100*positive/positive.loc["Total"]
    percentages = percentages.squeeze()
    remaining = sums.loc[percentages >= cutoff]
    consolidated = sums.loc[percentages < cutoff]
    if "Other" in remaining.index.tolist():
        remaining = remaining.copy(deep=True)
        remaining.loc["Other"] += consolidated.sum()
        return remaining
    if "Total" in consolidated.index.tolist():
        raise ValueError("Total got consolidated.")
    sum_df = pd.DataFrame([consolidated.sum()],
                          index=["Other"])
    out = pd.concat([remaining,sum_df])
    out = out.rename(columns = {out.columns[0]:'Value'})
    out.columns.name = 'Category'
    return out

def plot_net_cashflow(frame,
                      savepath=None,
                      show=True,
                      cutoff = 0.0):
    """Compares income and expenditures
    in bar chart

    Consolidates all values that are less than cutoff%
    of the total into "Other"
    """
    toplot = combine_expenses(frame,cutoff)
    labels = toplot.index.tolist()
    vals = toplot.as_matrix().flatten()
    plt.bar(labels,vals,
            color='b',
            alpha = 0.8)
    plt.xticks(rotation=90)
    plt.ylabel('Net Cashflow ($)')
    plt.xlabel('Category')
    if savepath:
        plt.savefig(savepath)
    if show:
        plt.show()
    return


