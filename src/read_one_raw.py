#! bin/env/ python
from pandas import DataFrame, Series
import pandas as pd
import numpy as np
import datetime as dt
import os
import sys


### Need to add Orb_Prof into data DF. Maybe create 105x1 and joining along
#vertical axis??

def read(mcs_file,profn0=0):
    '''
    Read in single MCS .TAB file (4 hours of single day)

    Inputs
    ------

    Outputs
    -------
    df: DataFrame, all profiles for single file
    meta_df: DataFrame, 1 row for each profile, Dates, LST, etc
    '''
    #find number of lines with comments
    #assuming only at the beginning
    #Also get date info
    comlines = 0
    date_info = []
    profn = int(profn0)
    proforb = 0 #initialize orit profile number
    orbno = 0 #initialize orbnumer
    with open(mcs_file) as f:
        for line in f.readlines():
            #count commented lines for reading in through pandas later
            if line.rstrip()[0] == '#':
                comlines+=1
            #get date lines, remove quotes and whitespace, make list, add to list
            elif '"' in line.rstrip():
                temp_list = line.rstrip().replace('"','').replace(' ','').split(',')
                if temp_list[6] == orbno:
                    proforb += 1
                else:
                    orbno = temp_list[6] #get orbnum
                    proforb = 1
                #convert relevant columns to floats, ints
                for i, x in enumerate(temp_list):
                    if ('.' in x) and (':' not in x): #values with decimals
                        temp_list[i] = float(x)
                    elif (':' not in x) and (len(x)!=0): #non UTC, empty
                        #ignore Dates
                        if len(x)<3:
                            temp_list[i] = int(x)
                        elif (x[2]!='-'):
                            temp_list[i] = int(x)
                        else:
                            pass
                    else:
                        pass
                temp_list += [profn,proforb] #attach prof number to info for meta-data line
                date_info.append(temp_list) #add to list of date rows
                profn += 1 #update profile number
            #get date info columns, remove whitespace, make list
            elif 'Date' in line.rstrip():
                date_cols= line.rstrip().replace(' ','').split(',')
            else:
                pass

    date_cols[0] = 'line_qual' #fix column labeled '1'
    date_cols += ['Prof#','Orb_Prof'] #Add profile number column to connect with data

    #rows of date lines (starts 2 after comments)
    datelines = range(comlines+2,100000,106) #105 data rows between new dates

    skips = range(comlines+1)+datelines #skip comments+date header, date lines

    #read in data
    #data for each point in profile
    df = pd.read_csv(
            mcs_file,skiprows=skips,header=0,delimiter=',',
            skipinitialspace=True,na_values=-9999)
    #meta-data for each profile
    meta_df = DataFrame(date_info,columns=date_cols)
    #deal with empty and NaNs
    meta_df = meta_df.replace('',np.NaN)
    meta_df = meta_df.replace('-9999',np.NaN)

    #connect meta_data to each row of profile
    profnum = df.index/105+profn0
    df['Prof#'] = profnum.astype(int)
    df = df.rename(columns={'1':'line_qual'})

    return df, meta_df

def save_data(filename):
    datafile = filename.split('/')
    filenamesplit = datafile[-1].split('_')
    ymdh = filenamesplit[0]
    ystr = ymdh[0:4]
    mstr = ymdh[4:6]
    dstr = ymdh[6:8]
    hstr = ymdh[8:10]
    data,meta = read(filename)
    proc_base = 'data/processed/mcs/mrom_2/'
    proc_path = proc_base+ystr+'/'+ystr+mstr+'/'+ystr+mstr+dstr+'/'
    meta_path = proc_path + 'meta/'
    data_path = proc_path + 'data/'

    #make directories...
    for newdir in [meta_path,data_path]:
        if not os.path.exists(newdir):
            print newdir
            os.makedirs(newdir)


    # Save files
    meta.to_csv(meta_path+ymdh+'.csv')

    print meta
    sys.exit()

    #split up data by profiles
    for name, group in data.groupby('Orb_Prof'):
        group.to_csv(data_path+name+'.csv')

if __name__ == '__main__':
    #run some tests in the future....
    print 'in read_one'

    testfile = 'data/raw/MCS/MROM_2/2015/201502/20150201/2015020100_DDR.TAB'
    save_data(testfile)
