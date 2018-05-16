#!env/bin python
# Marek Slipski
# 20180418
# 20180419

# Plot latitude and local time of each
# profile observation

import pandas as pd
import matplotlib.pyplot as plt

import loadfiles


#Obs Qual colors
def color_obs(obsqual):
    if obsqual == 0:
        return 'k'
    elif obsqual == 1:
        return 'lightgreen'
    elif obsqual == 2:
        return 'lightblue'
    elif obsqual == 3:
        return 'darkblue'
    elif obsqual == 4:
        return 'lightcoral'
    elif obsqual == 5:
        return 'darkred'
    elif obsqual == 6:
        return 'r'
    elif obsqual == 7:
        return 'purple'
    elif obsqual == 10:
        return 'gray'
    elif obsqual == 11:
        return 'darkgreen'
    else:
        print 'Obs_qual not recognized'
        return 0

if __name__=='__main__':
    parser = loadfiles.data_input_args() # enter files/profiles/data in command line
    parser.add_argument('-s','--save',action='store',
                       help='Save figure as')
    args = parser.parse_args() # get arguments
    ddf, mdf = loadfiles.data_input_parse(args) # convert input data to DFs    
    
    mdf['obs_col'] = mdf['Obs_qual'].apply(color_obs)

    plt.figure()
    plt.scatter(mdf['LTST']*24,mdf['Profile_lat'],color=list(mdf['obs_col']),s=8,alpha=0.5,lw=0)
    plt.xlabel('Local Time')
    plt.ylabel('Latitude')
    plt.xlim(0,24)
    plt.ylim(-90,90)

    plt.show()