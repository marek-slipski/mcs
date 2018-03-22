#! env/bin python
import glob
from pandas import DataFrame, Series
import pandas as pd
import datetime as dt

import os
import sys

# add the 'src' directory as one where we can import modules
src_dir = os.path.join(os.getcwd(), 'src')
sys.path.append(src_dir)

import read_one_raw
import filename_from_date as ffd

def read_files(
    start_year,start_month,start_day,end_year,end_month,end_day,datar='DDR'):
    '''
    Run read_one_file for many files. See that function for more info.
    4 hour files for each day

    *could use some stops or at least prints every once in awhile

    Inputs
    ------
    start_year/month/day: ints, start date
    end_year/month/day: ints, end date

    Outputs
    -------
    df: DataFrame, return all records
    meta_df: DataFrame, parameters fro single profiles
    '''
    profn = 0
    #convert start and end dates
    sd = dt.datetime(start_year,start_month,start_day,hour=0)
    ed = dt.datetime(end_year,end_month,end_day,hour=20)
    date = dt.datetime(start_year,start_month,start_day)
    df_pieces = [] #will concatenate many DataFrames together
    meta_pieces = []
    while (date >= sd) and (date <= ed): #do for each day
        file_name = ffd.get_filename(
                    date.year,date.month,date.day,date.hour,datar)

        if glob.glob(file_name): #if file exists...
            try:
                df_temp,meta_temp = read_one_raw.read(file_name,profn0=profn) #read in single file (4 hours)
            except Exception, e:
                print >> sys.stderr, "Problem with file: "+file_name
                print >> sys.stderr, "Exception: %s" % str(e)
                sys.exit(1)
            profn = int(meta_temp['Prof#'].max())+1
            df_pieces.append(df_temp) #add that to list to be concatenated
            meta_pieces.append(meta_temp)
        else:
            pass
        date += dt.timedelta(hours=4) #advance to next file (4-hr intervals)
    df = pd.concat(df_pieces,ignore_index=True) #after, join tables
    meta_df = pd.concat(meta_pieces,ignore_index=True)
    return df, meta_df
