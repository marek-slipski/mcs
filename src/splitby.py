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
    parser.add_argument('--lon',action='store',nargs=2,type=float,
                       help='Longitude range (degrees [-180,180])')
    parser.add_argument('--verbose','-v',action='store_true',
                       help='Print out all profile numbers returned')
    parser.add_argument('--save','-s',action='store',
                       help='Save returned profile numbers')
    parser.add_argument('--savecsv',action='store',
                       help='Save DataFrames as csv')
    
    args = parser.parse_args()
    
    ## Get path to data from config file
    with open('src/config.yaml') as cy:
        config = yaml.load(cy)
    path_base = config['data_path']
    with open(args.files,'rb') as inputfile:
        files =  [path_base+x.rstrip() for x in inputfile]
    
    # Initialize
    profn = 0
    data_pieces, meta_pieces = [], []
    
    # Loop through all files
    ftotal = len(files)
    print('\n'+str(ftotal)+' files to read')
    for i,infile in enumerate(files):
        if (i)%1000 == 0:
            print('\n'+str(i)+' / '+str(ftotal))
        # Try to read
        try:
            ddf,mdf = loadfiles.read(infile,profn0=profn) # data and metadata
        except IOError,e:
            print e
            continue # got to next file
    
        # Data and Meta DFs
        #ddf, mdf = loadfiles.open_combine(args.files)

        # For each parameter, find profiles meet criteria and update meta DF
        if args.lat:
            mdf = find_between(mdf,'Profile_lat',args.lat[0],args.lat[1])

        if args.lst: 
            mdf = find_between(mdf,'LTST',args.lst[0]/24,args.lst[1]/24)

        if args.lon:
            mdf = find_between(mdf,'Profile_lon',args.lon[0],args.lon[1])
            
        # If some profiles meet criteria, get corresponding data
        if mdf.empty:
            continue
        else:
            ddf = ddf[ddf['Prof#'].isin(mdf['Prof#'])] # keep only data from correct profiles
            data_pieces.append(ddf), meta_pieces.append(mdf) # add this file's DF to list
            profn = int(mdf['Prof#'].max(skipna=True))+1 # keep track of given unique Profile number
    
    # With all files read, convert lists of DFs to large DFs
    print('\nConcatenating data...')
    data = pd.concat(data_pieces,ignore_index=True)
    meta = pd.concat(meta_pieces,ignore_index=True)

    # Save Profile Numbers
    if args.save:
        with open(args.save,'wb') as sf:
            print >> sf, "\n".join(str(prof) for prof in meta['Prof#'])
    
    # Save DataFrames
    if args.savecsv:
        print('\nSaving DataFrames to '+args.savecsv+'_data.csv and '+args.savecsv+'_meta.csv')
        data.to_csv(args.savecsv+'_data.csv',index=False)
        meta.to_csv(args.savecsv+'_meta.csv',index=False)
    
    # Print Profile numbers
    if args.verbose:
        for prof in meta['Prof#']:
            print prof