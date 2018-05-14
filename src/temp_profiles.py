#!env/bin python
# Marek Slipski
# 20180419


# Plot termperature vs. altitude (or Pressure) for each 
# profile. Eventually plot mean, contours, etc.

import sys
import numpy as np
import pandas as pd
import argparse
import matplotlib.pyplot as plt

import loadfiles


parser = argparse.ArgumentParser(
    description='Determine input type')
parser.add_argument('files',nargs='+')
parser.add_argument('--type',action='store',choices=['fp','dfs'],
                   help='fp: Input is list of files (plot all files) or \
                   list of files and profile numbers to plot. \
                   dfs: Input is DataFrame of data or DataFrames of \
                   data and meta (will plot all profiles)')
parser.add_argument('--verbose','-v',action='store_true',
                   help='Display information')

args = parser.parse_args()

if not args.type:
    if args.files[0].split('.')[-1] == 'csv':
        if args.verbose:
            print 'Assuming arguments are the data and not lists of files'
        args.type = 'dfs'
    else:
        if args.verbose:
            print 'Assuming arguments are lists of files and not data'
        args.type = 'fp'

if args.type=='fp':
    if len(args.files) == 1:
        ddf, mdf = loadfiles.open_combine(args.files[0]) #open data and meta from all files
    elif len(args.files) == 2:
        ddf, mdf = loadfiles.open_profs(args.files[0],args.files[1]) #open and reduce
    else:
        sys.exit('Unrecognized third input. Try -h for help.')
        
elif args.type=='dfs':
    ddf = pd.read_csv(args.files[0]) #open data from frist input
    if len(args.files) == 1: #data already opened
        pass
    elif len(args.files) == 2: # use second file
        mdf = pd.read_csv(args.files[1]) #open metadata
    else:
        sys.exit('Unrecognized third input. Try -h for help.')
    
yaxis = 'Alt'

plt.figure()
for profnum, profdata in ddf.groupby('Prof#'):
    plt.plot(profdata['T'],profdata[yaxis],color='gray',alpha=0.3,lw=0.5)
    
plt.xlabel('Temperature [K]')
if yaxis == 'Alt':
    plt.ylabel('Altitude [km]')
elif yaxis == 'Pres':
    plt.ylabel('Pressure [Pa]')
    plt.yscale('log')
    plt.gca().invert_yaxis()
    
print 'Profiles shown:',len(mdf)    

plt.show()