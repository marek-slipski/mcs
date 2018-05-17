#!env/bin python
# Marek Slipski
# 20180514
# 20180516

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import argparse

import loadfiles

#import temp_fncs as tmp

if __name__=='__main__':
    parser = loadfiles.data_input_args() # enter files/profiles/data in command line
    parser.add_argument('-s','--save',action='store',
                       help='Save figure as')
    args = parser.parse_args() # get arguments
    ddf, mdf = loadfiles.data_input_parse(args) # convert input data to DFs
    
    bin_num_lon = 16
    
    # SETUP BINS and midpoints
    bins_lon = np.linspace(-180,180,bin_num_lon) #Longitude
    mids_lon = (bins_lon[0:-1] + bins_lon[1:])/2

    #yaxis = 'Alt'
    bins_alt = np.linspace(0,100,50) #Alitutde
    mids_alt =  (bins_alt[0:-1] + bins_alt[1:])/2

    # Prep data
    ddf.dropna(subset=['T','Lon','Alt'],inplace=True) # remove NaNs

    # Add columns noting bins
    ddf['Lon_bin'] = pd.cut(ddf['Lon'],bins_lon,labels=mids_lon) #longitude
    counts_lon = pd.value_counts(ddf['Lon_bin'])
    ddf['Alt_bin'] = pd.cut(ddf['Alt'],bins_alt,labels=mids_alt) #altitude
    # convert bin column mid point values to floats
    ddf[['Lon_bin','Alt_bin']] = ddf[['Lon_bin','Alt_bin']].apply(pd.to_numeric)

    # Calculate aggregates (means, stds, counts) in each bin
    binned_mean = ddf.groupby(['Lon_bin','Alt_bin'])['T'].mean()

    # Convert bins to 2d for contours
    # Mean
    binned_meanreset = binned_mean.reset_index()
    binned_meanreset.columns = ['Lon_bin', 'Alt_bin', 'T']
    binned_mean_pivot=binned_meanreset.pivot('Lon_bin', 'Alt_bin')
    X_mean=binned_mean_pivot.columns.levels[1].values
    Y_mean=binned_mean_pivot.index.values
    Z_mean=binned_mean_pivot.values
    Xi_mean,Yi_mean = np.meshgrid(X_mean, Y_mean)
    # STD
    binned_sd = ddf.groupby(['Lon_bin','Alt_bin'])['T'].std()
    binned_sd_reset = binned_sd.reset_index()
    binned_sd_reset.columns = ['Lon_bin', 'Alt_bin', 'T']
    binned_sd_pivot=binned_sd_reset.pivot('Lon_bin', 'Alt_bin')
    X_std=binned_sd_pivot.columns.levels[1].values
    Y_std=binned_sd_pivot.index.values
    Z_std=binned_sd_pivot.values
    Xi_std,Yi_std = np.meshgrid(X_std, Y_std)
    
    # For individual bin profiles
    t_df = pd.DataFrame(binned_mean) # Temperature
    t_df.reset_index(inplace=True)
    sd_df = pd.DataFrame(binned_sd) # Standard Deviations
    sd_df.reset_index(inplace=True)


    # Create large plot
    lfig, lax = plt.subplots(2,2,figsize=(12,12))
    # x and y limits
    y1 = 10
    y2 = 90
    t1 = 120
    t2 = 220
    s1 = 0
    s2 = 15
    
    # Temp Contour
    ctc = lax[0,0].contourf(Yi_mean,Xi_mean,Z_mean,np.linspace(t1,t2,21),vmin=t1,vmax=t2)
    tbar = lfig.colorbar(ctc,ax=lax[0,0],label='Temperature [K]')
    lax[0,0].set_xlabel(r'Longitude ($^{\circ}$)')
    lax[0,0].set_ylabel('Altitude [km]')
    lax[0,0].set_ylim(y1,y2)
    lax[0,0].set_xlim(-181,181)

    # STD Contour
    csc = lax[0,1].contourf(Yi_std,Xi_std,Z_std,np.linspace(s1,s2,16),vmin=s1,vmax=s2)
    sbar = lfig.colorbar(csc,ax=lax[0,1],label='Standard Deviation [K]')
    lax[0,1].set_ylim(y1,y2)
    lax[0,1].set_xlabel(r'Longitude ($^{\circ}$)')
    lax[0,1].set_ylabel('Altitude [km]')
    lax[0,1].set_xlim(-181,181)
    
    # Temp profiles
    styles = ['k','gray','cyan','b','r','lightcoral','darkorange','purple','yellow','seaborn']
    for i,lon in enumerate(sd_df['Lon_bin'].unique()[1::2]):
        # Draw vertical lines in contours
        lax[0,0].plot([lon,lon],[0,100],color=styles[i],ls='--')
        lax[0,1].plot([lon,lon],[0,100],color=styles[i],ls='--')
        tex = t_df[t_df['Lon_bin']==lon].dropna() # temperature
        sex = sd_df[sd_df['Lon_bin']==lon] # std
        lax[1,0].plot(tex['T'],tex['Alt_bin'],color=styles[i]) #plot T
        lax[1,1].plot(sex['T'],sex['Alt_bin'],color=styles[i]) # plot STD
        
        
        #dz = np.gradient(tex['Alt_bin']*1000)
        #N2 = tmp.wB_freq(tex['Alt_bin']*1000,tex['T'])
        
        #ta.plot(tex['T'],tex['Alt_bin'])
        #sda.plot(ex['T'],ex['Alt_bin'])
        #N2a.plot(N2,tex['Alt_bin'])
    
    # Means over all Longitudes
    Tm = ddf.groupby('Alt_bin')['T'].mean()
    Ts = ddf.groupby('Alt_bin')['T'].std()
    Tsmean = sd_df.groupby('Alt_bin')['T'].mean()
    diff = Ts - Tsmean
    print diff[(diff.index<80)&(diff.index>20)].min(), diff[(diff.index<80)&(diff.index>20)].max(), diff[(diff.index<80)&(diff.index>20)].mean()
    lax[1,0].plot(Tm,Tm.index,c='k',lw=3,ls='--')
    lax[1,1].plot(Ts,Ts.index,'k',lw=3,ls='--')
    lax[1,1].plot(Tsmean,Tsmean.index,'k',lw=3,ls=':')
    
    #Axes
    lax[1,0].set_ylim(y1,y2)
    lax[1,0].set_xlim(t1,t2)
    lax[1,0].set_xlabel('Temperature [K]')
    lax[1,0].set_ylabel('Altitude [km]')
    
    lax[1,1].set_ylim(y1,y2)
    lax[1,1].set_xlim(s1,s2)
    lax[1,1].set_xlabel('Standard Deviation [K]')
    lax[1,1].set_ylabel('Altitude [km]')


    #Tm = ddf.groupby('Alt_bin')['T'].mean()
    #Ts = ddf.groupby('Alt_bin')['T'].std()
    #Tmed = ddf.groupby('Alt_bin')['T'].median()
    #Tslon = sd_df.groupby('Alt_bin')['T'].mean()

    #sda.plot(Ts,Ts.index,'k',lw=1)
    #sda.plot(Tslon,Tslon.index,'k',lw=2)
    #ta.errorbar(Tm,Tm.index,xerr=Ts,c='gray',lw=3)
    #ta.plot(Tm,Tm.index,c='gray',lw=3)
    #ta.plot(Tmed,Tmed.index,'k',lw=3)

    
    if args.save:
        plt.savefig(args.save,dpi=300)


    plt.show()