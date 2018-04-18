import pandas as pd
import matplotlib.pyplot as plt

import loadfiles

# Data and Meta DFs
ddf, mdf = loadfiles.ddf, loadfiles.mdf


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
    
mdf['obs_col'] = mdf['Obs_qual'].apply(color_obs)

plt.figure()
plt.scatter(mdf['LTST']*24,mdf['Profile_lat'],color=list(mdf['obs_col']),s=5)
plt.xlabel('Local Time')
plt.ylabel('Latitude')
plt.xlim(0,24)
plt.ylim(-90,90)

plt.show()