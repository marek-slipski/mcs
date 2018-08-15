#!env/bin python
# Marek Slipski
# 20180514

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import argparse

import loadfiles

import temp_fncs as tmp

#####################################################
# Script to make contours of T, sig_T, and N^2 
# as a function of Alt or Pressure
#
#####################################################

def convert_2d(df,cols):
    '''
    Convert Grouped/Binned DataFrame to 2d array to use for
    contour plot.
    
    Inputs
    ------
    df: DataFrame with at least 2 cols (x, y) (values are aggregated)
    cols: list, [x,y] names of columns 
    
    Outputs
    -------
    Xi, Yi, Z: np.meshgrid, 2d array of x, y, and z
    
    Example:
    binned_mean = ddf.groupby(['Lon_bin','Alt_bin'])['T'].mean()
    Xi, Yi, Z = convert_2d(binned_mean,['Lon_bin','Alt_bin'])
    '''
    dfreset = df.reset_index()
    df_pivot=dfreset.pivot(cols[0], cols[1])
    X=df_pivot.columns.levels[1].values
    Y=df_pivot.index.values
    Z=df_pivot.values
    Xi,Yi = np.meshgrid(X, Y)
    return Xi, Yi, Z
    

if __name__=='__main__':
    ## PARSE INPUTS
    parser = loadfiles.data_input_args() # enter files/profiles/data in command line
    plotparse = parser.add_argument_group('Plotting Arguments')
    # Plotting arguments
    plotparse.add_argument('-s','--save',action='store',
                           help='Save figure as')
    plotparse.add_argument('--hide',action='store_true',default=False,
                           help='Hide figure')
    plotparse.add_argument('-x','--xaxis',action='store',choices=['lat','lon','lst','Ls','sza'],
                           default='lon',
                           help='X-axis units')
    plotparse.add_argument('-y','--yaxis',action='store',choices=['Alt','Pres'],default='Alt',
                           help='Y-axis units')
    plotparse.add_argument('--xbins',action='store',default=15,type=int,
                           help='Number of bins in x (default=16)')
    plotparse.add_argument('--ybins',action='store',default=50,type=int,
                           help='Number of bins in y [Alt/Pres] (default=50)')
    args = parser.parse_args() # get arguments
    
    ## LOAD DATA
    print '==loading data'
    ddf, mdf = loadfiles.data_input_parse(args) # convert input data to DFs
    mdf.set_index('Prof#',inplace=True)
    
    ## Axis Prep    
    ycol = args.yaxis # Alt or Pres column name
    ybincol = ycol+'_bin' # make bin in column name
    # Setup Y-axis plotting parameters
    yplot = {'Alt':{'label':'Altitude [km]','lim':[0,100],'scale':'linear'}, 
             'Pres':{'label':'Pressure [Pa]','lim':[1.e+3,5.e-3],'scale':'log'}}
    
    xcol = args.xaxis
    xnames = {'lon':'Lon','lst':'LTST','lat':'Lat','Ls':'L_s','sza':'Solar_zen'} # conversion to actual col name
    xshort = xnames[xcol] # shortcut to column name
    xbins = {'lon':[-180,180],'lst':[0,1],'lat':[-90,90],'Ls':[-10,370],'sza':[0,180]} # bin ranges
    xbincol = xshort+'_bin'
    # Setup X-axis plotting parameters
    xplot = {'lon':{'label':r'Longitude ($^{\circ}$)','lim':[-181,181]},
             'lst':{'label':'Local Solar Time (hr/24)','lim':[-0.01,1.01]},
             'lat':{'label':r'Latitude ($^{\circ}$)','lim':[-91,91]},
             'Ls':{'label':r'$L_s$ ($^{\circ}$)','lim':[-1,361]},
             'sza':{'label':r'SZA ($^{\circ}$)','lim':[-1,181]}
            }
    
    ## SETUP BINS 
    print '==binning'
    # X-bins
    bins_lon = np.linspace(xbins[xcol][0],xbins[xcol][1],args.xbins+1) # longitude
    mids_lon = (bins_lon[0:-1] + bins_lon[1:])/2 # midpoints

    # Y-bins
    if ycol == 'Alt':
        #bins_y = np.linspace(ddf[ycol].min(),ddf[ycol].max(),args.ybins+1) # alitutde
        bins_y = np.linspace(0,100,args.ybins+1) # alitutde
        mids_y =  (bins_y[0:-1] + bins_y[1:])/2 # midpoints
    else:
        bins_y = np.geomspace(ddf[ycol].min(),ddf[ycol].max(),args.ybins+1) # alitutde
        mids_y =  (bins_y[0:-1] + bins_y[1:])/2 # midpoints

    ## BIN DATA
    if xcol == 'lst' or xcol == 'Ls' or xcol=='sza':
        ddf[xshort] = ddf['Prof#'].apply(lambda x: mdf.at[x,xshort])
        
    ddf.dropna(subset=['T',xshort,ycol],inplace=True) # remove NaNs
    
     
    # Add columns noting bins
    ddf[xbincol] = pd.cut(ddf[xshort],bins_lon,labels=mids_lon) #longitude
    ddf[ybincol] = pd.cut(ddf[ycol],bins_y,labels=mids_y) # altitude
    # convert bin column mid point values to floats
    ddf[[xbincol,ybincol]] = ddf[[xbincol,ybincol]].apply(pd.to_numeric)
    
    # Calculate aggregates (means, stds, counts) in each bin
    binned_mean = ddf.groupby([xbincol,ybincol])['T'].mean() #temp 
    alt_mean = ddf.groupby([xbincol,ybincol])['Alt'].mean() #alt for N2
    binned_N2 = tmp.wB_freq(alt_mean*1000,binned_mean) #N2
    binned_sd = ddf.groupby([xbincol,ybincol])['T'].std() #std
    binned_count = ddf.groupby([xbincol,ybincol])['T'].count() # counts
        
        
    # PREP FOR PLOTTING
    Xi_mean, Yi_mean, Z_mean = convert_2d(binned_mean,[xbincol,ybincol]) #temp   
    Xi_N2, Yi_N2, Z_N2 = convert_2d(binned_N2, [xbincol,ybincol]) # N2
    Xi_std, Yi_std, Z_std = convert_2d(binned_sd, [xbincol,ybincol]) #std
    Xi_count, Yi_count, Z_count = convert_2d(binned_count, [xbincol,ybincol]) #couns
    

    # Create large plot
    print '==plotting contours'
    lfig, lax = plt.subplots(2,4,figsize=(22,9))
    # X and Y limits
    y1, y2 = yplot[ycol]['lim']
    t1 = 110
    t2 = 250
    s1 = 0
    s2 = 20
    c1 = 30
    c2 = binned_count.max()
    Nm = 0.4e-4*1.e+4
    Nx = 2.5e-4*1.e+4
    
    ## CONTOURS (TOP ROW)
    # Temp Contour
    ctc = lax[0,0].contourf(Yi_mean,Xi_mean,Z_mean,np.linspace(t1,t2,21))
    tbar = lfig.colorbar(ctc,ax=lax[0,0],label='Temperature [K]')
    lax[0,0].set_xlabel(xplot[xcol]['label'])
    lax[0,0].set_ylabel(yplot[ycol]['label'])
    lax[0,0].set_ylim(y1,y2)
    lax[0,0].set_yscale(yplot[ycol]['scale'])
    lax[0,0].set_xlim(xplot[xcol]['lim'])
    lax[0,0].text(xplot[xcol]['lim'][0]+20,y2-6,'a',fontsize=12)

    # STD Contour
    csc = lax[0,1].contourf(Yi_std,Xi_std,Z_std,np.linspace(s1,s2,21))
    sbar = lfig.colorbar(csc,ax=lax[0,1],label='Standard Deviation [K]')
    lax[0,1].set_ylim(y1,y2)
    lax[0,1].set_xlabel(xplot[xcol]['label'])
    lax[0,1].set_ylabel(yplot[ycol]['label'])
    lax[0,1].set_yscale(yplot[ycol]['scale'])
    lax[0,1].set_xlim(xplot[xcol]['lim'])
    lax[0,1].text(xplot[xcol]['lim'][0]+20,y2-6,'b',fontsize=12)
    
    # N2 Contour
    cNc = lax[0,2].contourf(Yi_N2,Xi_N2,Z_N2*1.e+4,np.linspace(Nm,Nx,16))
    Nbar = lfig.colorbar(cNc,ax=lax[0,2],label=r'$N^2 x 1.0\times10^4$ [s$^{-2}$]')
    lax[0,2].set_ylim(y1,y2)
    lax[0,2].set_xlabel(xplot[xcol]['label'])
    lax[0,2].set_ylabel(yplot[ycol]['label'])
    lax[0,2].set_yscale(yplot[ycol]['scale'])
    lax[0,2].set_xlim(xplot[xcol]['lim'])
    lax[0,2].text(xplot[xcol]['lim'][0]+20,y2-6,'c',fontsize=12)
    
    # Counts Contour
    ccc = lax[0,3].contourf(Yi_count,Xi_count,Z_count,np.linspace(c1,c2,16))
    cbar = lfig.colorbar(ccc,ax=lax[0,3],label='Number of Profiles')
    lax[0,3].set_ylim(y1,y2)
    lax[0,3].set_xlabel(xplot[xcol]['label'])
    lax[0,3].set_ylabel(yplot[ycol]['label'])
    lax[0,3].set_yscale(yplot[ycol]['scale'])
    lax[0,3].set_xlim(xplot[xcol]['lim'])
    
    ## LOOP THROUGH INDIVIDUAL LONG BINS (BOTTOM ROW)
    print '==plotting individual profiles'
    # For individual bin profiles
    
    t_df = pd.DataFrame(binned_mean).reset_index() # Temperature
    alt_df = pd.DataFrame(alt_mean).reset_index() #alt for N^2
        
    t_alt = pd.merge(t_df, alt_df,on=[xbincol,ybincol]) #alt and T for N^2
    #t_df.reset_index(inplace=True)
    t_alt.reset_index(inplace=True)
    sd_df = pd.DataFrame(binned_sd) # Standard Deviations
    sd_df.reset_index(inplace=True)
    c_df = pd.DataFrame(binned_count) # Counts
    c_df.reset_index(inplace=True)
    styles = ['k','gray','cyan','b','r','lightcoral','darkorange',
              'purple','yellow','g'] + ['k']*20
    for i,lon in enumerate(sd_df[xbincol].unique()[1::2]):
        # Draw vertical lines in contours
        #lax[0,0].plot([lon,lon],[0,1000],color=styles[i],ls='--')
        #lax[0,1].plot([lon,lon],[0,1000],color=styles[i],ls='--')
        #lax[0,2].plot([lon,lon],[0,1000],color=styles[i],ls='--')
        tex = t_df[t_df[xbincol]==lon].dropna() # temperature
        altex = t_alt[t_alt[xbincol]==lon].dropna() # alt
        sex = sd_df[sd_df[xbincol]==lon] # std
        lax[1,0].plot(tex['T'],tex[ybincol],color=styles[i]) #plot T
        lax[1,1].plot(sex['T'],sex[ybincol],color=styles[i]) # plot STD
        # Calculate Brunt-Vaisalla Frequency
        N2 = tmp.wB_freq(altex['Alt']*1000,altex['T'])
        lax[1,2].plot(N2*1.e+4,altex[ybincol],color=styles[i])
        
    
    # Means over all Longitudes
    Tm = ddf.groupby(ybincol)['T'].mean()# temp over all
    Am = ddf.groupby(ybincol)['Alt'].mean() #salt over all
    N2m = tmp.wB_freq(Am*1000,Tm).reset_index() # N2 over all 
    Ts = ddf.groupby(ybincol)['T'].std().reset_index() # Std over all
    Tsmean = sd_df.groupby(ybincol)['T'].mean() #mean of std bins
    diff = Ts - Tsmean # difference between std over all and mean std 
    
    ## Axes and mean profiles
    # TEMPERATURE
    lax[1,0].plot(Tm,Tm.index,c='k',lw=3,ls='--') # meanT over all long
    lax[1,0].set_ylim(y1,y2)
    lax[1,0].set_xlim(t1,t2)
    lax[1,0].set_xlabel('Temperature [K]')
    lax[1,0].set_ylabel(yplot[ycol]['label'])
    lax[1,0].set_yscale(yplot[ycol]['scale'])
    
    # STANDARD DEVIATIONS
    lax[1,1].plot(Ts,Ts.index,'k',lw=3,ls='--') # std over all long
    lax[1,1].plot(Tsmean,Tsmean.index,'k',lw=3,ls=':') # mean std over bins
    lax[1,1].set_ylim(y1,y2)
    lax[1,1].set_xlim(s1,s2)
    lax[1,1].set_xlabel('Standard Deviation [K]')
    lax[1,1].set_ylabel(yplot[ycol]['label'])
    lax[1,1].set_yscale(yplot[ycol]['scale'])

    # BRUNT-VAISALLA FREQ
    lax[1,2].plot(N2m*1.e+4,Am.index,'k',lw=3,ls='--') #mean N2 over all long
    lax[1,2].set_ylim(y1,y2)
    lax[1,2].set_xlim(Nm,Nx)
    lax[1,2].set_xlabel(r'$N^2 x 1.0\times10^4$ [s$^{-2}$]')
    lax[1,2].set_ylabel(yplot[ycol]['label'])
    lax[1,2].set_yscale(yplot[ycol]['scale'])
    
    lfig.tight_layout()
    
    # PLOTTING OPTIONS
    if args.save:
        print '==saving figure'
        plt.savefig(args.save,dpi=500)

    if not args.hide:
        plt.show()
        
    #maxN2 = 2.1e-04    
        
    #print Ts[(Ts['Alt_bin']>=50) & (Ts['Alt_bin']<80)].mean()
    #print N2m[0][(N2m['Alt_bin']>=50) & (N2m['Alt_bin']<80)].mean()/maxN2
    #print Tm.coulmns
    Tm = Tm.reset_index()
    print Tm[(Tm['Alt_bin']>=68) & (Tm['Alt_bin']<72)].mean()