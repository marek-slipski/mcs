#!env/bin/ python
# Marek Slipski
# 20180419

# Need to be able to split by some criteria
# lat/lst/long/etc.
# and grab just those profiles in dataset
# Then other scripts can take in argument and select
# just those profiles

import pandas as pd
import yaml

import loadfiles

# Data and Meta DFs
ddf, mdf = loadfiles.ddf, loadfiles.mdf

#SPLIT CONDITIONS (read from config file?)
with open('src/config.yaml') as cy:
    config = yaml.load(cy)
latmin=config['latmin']
latmax=config['latmax']
lstmin=config['lstmin']/24.
lstmax=config['lstmax']/24.

latcond = (mdf['Profile_lat']>latmin) & (mdf['Profile_lat']<latmax)
lstcond = (mdf['LTST']>lstmin) & (mdf['LTST']<lstmax)
red_df = mdf[latcond&lstcond]

for prof in red_df['Prof#']:
    print prof