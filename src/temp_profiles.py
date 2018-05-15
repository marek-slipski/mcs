#!env/bin python
# Marek Slipski
# 20180419
# 20180515


# Plot termperature vs. altitude (or Pressure) for each 
# profile. Eventually plot mean, contours, etc.

import sys
import numpy as np
import pandas as pd
import argparse
import matplotlib.pyplot as plt

import loadfiles

if __name__=='__main__':
    parser = loadfiles.data_input_args() # enter files/profiles/data in command line
    args = parser.parse_args() # get arguments
    ddf, mdf = loadfiles.data_input_parse(args) # convert input data to DFs


    yaxis = 'Alt'

    plt.figure()
    
    # Plot each profiles
    for profnum, profdata in ddf.groupby('Prof#'):
        plt.plot(profdata['T'],profdata[yaxis],color='gray',alpha=0.3,lw=0.5)

    
    # Axes
    plt.xlabel('Temperature [K]')
    if yaxis == 'Alt':
        plt.ylabel('Altitude [km]')
    elif yaxis == 'Pres':
        plt.ylabel('Pressure [Pa]')
        plt.yscale('log')
        plt.gca().invert_yaxis()

    print 'Profiles shown:',len(mdf)    

    plt.show() 