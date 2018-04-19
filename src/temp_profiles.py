#!env/bin python
# Marek Slipski
# 20180419

# FIRST - need to split data (by lat, lst, etc)
# and use just those profile numbers

# Plot termperature vs. altitude for each 
# profile. Eventually plot mean, contours, etc.

import pandas as pd
import matplotlib.pyplot as plt

import loadfiles

# Data and Meta DFs
ddf, mdf = loadfiles.ddf, loadfiles.mdf

plt.figure()
for profnum, profdata in ddf.groupby('Prof#'):
    plt.plot(profdata['T'],profdata['Alt'],color='gray',alpha=0.3,lw=0.5)
    
plt.xlabel('Temperature [K]')
plt.xlabel('Altitude [km]')

plt.show()