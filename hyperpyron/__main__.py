#!/usr/bin/env python

"""
hyperpyron/__main__.py
Author: Jonah Miller (jonah.maxwell.miller@gmail.com)
"""

# python
import sys,os
from os import path
import argparse
import importlib
from datetime import date,timedelta,datetime

# hyperpyron
import hyperpyron
from hyperpyron import iconfig
from hyperpyron import analysis
from hyperpyron import hyperparse
from hyperpyron.sysdirs import cache_dir,conf_dir,parse_conf_dir
from hyperpyron.budget import get_budget

def main():
    """The hyperpyron CLI interface"""
    
    parser = argparse.ArgumentParser(
        description = ("Take your finance into your hands!"
                       +" Reads in your plaintext configuration files"
                       +" and bank-provided financial data and generates"
                       +" analysis plots."),
        epilog = ("See https://github.com/Yurlungur/hyperpyron"
                  +" for configuration details."))
    # TODO: implement meaningful verbosity
    # parser.add_argument('-v','--verbose',
    #                     dest='verbose',
    #                     action="store_true",
    #                 help='Increases output verbosity')
    parser.add_argument('-i','--init',
                        dest='init',
                        action="store_true",
                        help=('Generates configuration directories,'
                              +' prints their location,'
                              +' and then quits.'
                              +' It is recommended that you do this first.'))
    parser.add_argument('-r','--reload',
                        dest='reload',
                        action="store_true",
                        help=('Forces Hyperpyron to reload financial data'
                              +' from file rather than using internal cache.'))
    parser.add_argument('-s','--save',
                        dest='savedir',
                        type=str,
                        help=('Instructs Hyperpyron to save its plots'
                              +' in the target directory.'))
    parser.add_argument('--hide',
                        dest='hide',
                        action="store_true",
                        help=("Hides the plots. If '-s' is set,"
                              +' the plots are still generated and saved.'))
    parser.add_argument('-p','--percentages',
                        dest='percentages',
                        action="store_true",
                        help=("Plots percent expenditures"))
    parser.add_argument('-f','--cashflow',
                        dest='cashflow',
                        action="store_true",
                        help=("Plots net cashflow"))
    parser.add_argument('-u','--budget',
                        dest='budget',
                        action="store_true",
                        help=("Compares net cashflow to budget."))
    parser.add_argument('-d','--days',
                        type=int,
                        dest='ndays',
                        default=-1,
                        help=('Selects and analysis data between'
                              +' N days in the past and now.'
                              +' default is for all time.'))
    parser.add_argument('-b','--between',
                        dest='between',
                        type=str,
                        nargs=2,
                        help=("Selects between two dates."
                              " each date should be of the form"
                              " 'yyyy-mm-dd'."))
    parser.add_argument('-c','--consolidate',
                        dest='minpercentage',
                        type=float,
                        default=0.0,
                        help=('In plots, consolidates all data less than'
                              +' minpercentage into the "Other" category.'))
    parser.add_argument('--pdf',
                        dest='pdf',
                        action='store_true',
                        help="Saves plots as pdfs instead of pngs.")
                        
    if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()

    print("Welcome to Hyperpyron! Take your finances into your own hands!")
    # init
    if args.init:
        print("Hyperpyron uses the following directories:")
        print("\tcache directory:",cache_dir)
        print("\tconfig directory:",conf_dir)
        print("\tparser config directory:",parse_conf_dir)
        print("They have been created if they did not already exist.")
        sys.exit(os.EX_OK)
    # ensure consistency
    if args.minpercentage < 0 or args.minpercentage > 100:
        print("Consolidation must be a percentage between 0 and 100.")
        sys.exit(os.EX_DATAERR)
    if args.savedir and not os.path.isdir(args.savedir):
        print("Path {} is not a valid directory.".format(args.savepath))
        sys.exit(os.EX_DATAERR)
    # load data
    if args.reload:
        frame = hyperparse.parse_from_data()
        print("Loaded data from files.")
    else:
        frame = hyperparse.load_from_cache()
        if frame is None:
            frame = hyperparse.parse_from_data()
            print("Loaded data from files.")
        else:
            print("Loaded data from cache.")
    hyperparse.save_to_cache(frame)
    # figure date cuts
    before,after=None,None
    if args.ndays > -1:
        before,after = analysis.get_dates_for_n_days_ago_and_now(args.ndays)
    if args.between:
        before = datetime.strptime(args.between[0],
                                   '%Y-%m-%d')
        after = datetime.strptime(args.between[1],
                                  '%Y-%m-%d')
    if before and after:
        frame = analysis.filter_frame_between_dates(frame,
                                                    before,
                                                    after)
        print("Using data from",before,"to",after)

    # plots
    show = not args.hide
    if args.pdf:
        suffix='.pdf'
    else:
        suffix='.png'
    if args.percentages:
        if args.savedir:
            savepath = path.join(args.savedir,
                                 iconfig.PERCENT_FILENAME+suffix)
        else:
            savepath=None
        analysis.plot_percent_expenditures(frame,savepath,
                                           show,args.minpercentage)
    if args.cashflow:
        if args.savedir:
            savepath = path.join(args.savedir,
                                 iconfig.CASHFLOW_FILENAME+suffix)
        else:
            savepath=None
        analysis.plot_net_cashflow(frame,savepath,show,
                                   args.minpercentage)
    if args.budget:
        if args.savedir:
            savepath = path.join(args.savedir,
                                 iconfig.BUDGET_FILENAME+suffix)
        else:
            savepath=None
        budget = get_budget()
        analysis.compare_cashflow_to_budget(frame,budget,
                                            savepath,show)
    print("All done!")

if __name__ == "__main__":
    main()
