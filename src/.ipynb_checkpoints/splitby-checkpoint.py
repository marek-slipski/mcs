#!env/bin/ python
# Marek Slipski
# 20180419
# 20180427

# Need to be able to split by some criteria
# Redo this only open metadata

import pandas as pd
import yaml
import argparse

import loadfiles

# Not cyclic yet in LST

def find_between(meta,column,val1,val2):
    cond = (meta[column]>val1) & (meta[column]<val2)
    return meta[cond]

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='To split MCS data by lat, lst, etc.')
    parser.add_argument('files',
                       help='File of list of MCS filenames to search through')
    parser.add_argument('--lat',action='store',nargs=2,type=float,
                       help='Latitude range (degrees) [-90, 90]')
    parser.add_argument('--lst',action='store',nargs=2,type=float,
                       help='Local Solar Time (hours) [0,24]')
    parser.add_argument('--verbose','-v',action='store_true',
                       help='Print out all profile numbers returned')
    parser.add_argument('--save','-s',action='store',
                       help='Save returned profile numbers')
    parser.add_argument('--savecsv',action='store',
                       help='Save DataFrames as csv')
    
    args = parser.parse_args()
    
    # Data and Meta DFs
    ddf, mdf = loadfiles.open_combine(args.files)

    # For each parameter, reduce the table
    if args.lat:
        mdf = find_between(mdf,'Profile_lat',args.lat[0],args.lat[1])
        print mdf['Prof#']
    
    if args.lst: 
        mdf = find_between(mdf,'LTST',args.lst[0]/24,args.lst[1]/24)
        print mdf['Prof#']

    if args.save:
        with open(args.save,'wb') as sf:
            print >> sf, "\n".join(str(prof) for prof in mdf['Prof#'])
            
    if args.savecsv:
        ddf = ddf[ddf['Prof#'].isin(mdf['Prof#'])]
        ddf.to_csv(args.savecsv+'_data.csv',index=False)
        mdf.to_csv(args.savecsv+'_meta.csv',index=False)
    
    if args.verbose:
        for prof in mdf['Prof#']:
            print prof