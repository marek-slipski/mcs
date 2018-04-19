#!env/bin python
# Marek Slipski
# 20180418
# 20180419

# read in list of MCS data files
# create 2 dataframes, one for
# data bout each profile and one
# of data from each each profile

import pandas as pd
import numpy as np
import sys

#### READ AND COMBINE FUNCTIONS

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
    meta_df = pd.DataFrame(date_info,columns=date_cols)
    #deal with empty and NaNs
    meta_df = meta_df.replace('',np.NaN)
    meta_df = meta_df.replace('-9999',np.NaN)

    #connect meta_data to each row of profile
    profnum = df.index/105+profn0
    df['Prof#'] = profnum.astype(int)
    df = df.rename(columns={'1':'line_qual'})

    return df, meta_df

def combine(filelist):
    '''
    Generate dataframes for data and metadata from one or more files
    
    Inputs
    ------
    filelist: list, list of files to read
    
    Outputs
    -------
    data: DataFrame, all profiles
    meta: DataFrame, meta data for each profile
    '''
    profn = 0
    data_pieces, meta_pieces = [], []
    for f in filelist:
        ddf,mdf = read(f,profn0=profn)
        data_pieces.append(ddf), meta_pieces.append(mdf)
        profn = int(mdf['Prof#'].max())+1
    data = pd.concat(data_pieces,ignore_index=True)
    meta = pd.concat(meta_pieces,ignore_index=True)
    return data, meta

#############################################################
#############################################################

# OPEN FILES AND COMBINE
with open(sys.argv[1],'rb') as infile:
    files = [x.rstrip() for x in infile.readlines()]

ddf, mdf = combine(files)

