#!env/bin python
# Marek Slipski
# 20180419


# Plot termperature vs. altitude for each 
# profile. Eventually plot mean, contours, etc.

import sys
import pandas as pd
import matplotlib.pyplot as plt

import loadfiles

# Data and Meta DFs
ddf, mdf = loadfiles.ddf, loadfiles.mdf

# only for given profiles
if len(sys.argv) >2: # profile file given after files to load
    with open(sys.argv[2]) as proflist: 
        profiles = [x.rstrip() for x in proflist.readlines()]

    ddf = ddf[ddf['Prof#'].isin(profiles)] # reduce DataFrames
    mdf = mdf[mdf['Prof#'].isin(profiles)]
    
    
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

plt.show()