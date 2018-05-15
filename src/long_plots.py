#!env/bin python
# Marek Slipski
# 20180514

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import argparse

import loadfiles

#import temp_fncs as tmp

parser = argparse.ArgumentParser(description='Determine input type')
parser.add_argument('files',nargs='+')
parser.add_argument('--type',action='store',choices=['fp','dfs'],
                   help='fp: Input is list of files (plot all files) or \
                   list of files and profile numbers to plot. \
                   dfs: Input is DataFrame of data or DataFrames of \
                   data and meta (will plot all profiles)')
parser.add_argument('--verbose','-v',action='store_true',
                   help='Display information')

args = parser.parse_args()

if not args.type:
    if args.files[0].split('.')[-1] == 'csv':
        if args.verbose:
            print 'Assuming arguments are the data and not lists of files'
        args.type = 'dfs'
    else:
        if args.verbose:
            print 'Assuming arguments are lists of files and not data'
        args.type = 'fp'

if args.type=='fp':
    if len(args.files) == 1:
        ddf, mdf = loadfiles.open_combine(args.files[0]) #open data and meta from all files
    elif len(args.files) == 2:
        ddf, mdf = loadfiles.open_profs(args.files[0],args.files[1]) #open and reduce
    else:
        sys.exit('Unrecognized third input. Try -h for help.')
        
elif args.type=='dfs':
    ddf = pd.read_csv(args.files[0]) #open data from frist input
    if len(args.files) == 1: #data already opened
        pass
    elif len(args.files) == 2: # use second file
        mdf = pd.read_csv(args.files[1]) #open metadata
    else:
        sys.exit('Unrecognized third input. Try -h for help.')
    
# SETUP BINS and midpoints
bins_lon = np.linspace(-180,180,16) #Longitude
mids_lon = (bins_lon[0:-1] + bins_lon[1:])/2

#yaxis = 'Alt'
bins_alt = np.linspace(0,100,100) #Alitutde
mids_alt =  (bins_alt[0:-1] + bins_alt[1:])/2

# Prep data
ddf.dropna(subset=['T','Lon','Alt'],inplace=True) # remove NaNs

# Add columns noting bins
ddf['Lon_bin'] = pd.cut(ddf['Lon'],bins_lon,labels=mids_lon) #longitude
counts_lon = pd.value_counts(ddf['Lon_bin'])
ddf['Alt_bin'] = pd.cut(ddf['Alt'],bins_alt,labels=mids_alt) #altitude
counts_alt = pd.value_counts(ddf['Alt_bin'])
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




# Plots
plt.figure()
plt.contourf(Yi_mean,Xi_mean,Z_mean)
plt.colorbar()
plt.xlabel('Longitude')
plt.ylabel('Altitude')


Xi_std,Yi_std = np.meshgrid(X_std, Y_std)
plt.figure()
plt.contourf(Yi_std,Xi_std,Z_std)
plt.colorbar()
plt.ylim(10,90)
plt.xlabel('Longitude')
plt.ylabel('Altitude')


sd_df = pd.DataFrame(binned_sd)
sd_df.reset_index(inplace=True)

t_df = pd.DataFrame(binned_mean)
t_df.reset_index(inplace=True)

sdf,sda=plt.subplots()
tf,ta=plt.subplots()
#N2f, N2a = plt.subplots()

for i in sd_df['Lon_bin'].unique():
    ex = sd_df[sd_df['Lon_bin']==i]
    sda.plot(ex['T'],ex['Alt_bin'])
    tex = t_df[t_df['Lon_bin']==i].dropna()
    dz = np.gradient(tex['Alt_bin']*1000)
    #N2 = tmp.wB_freq(tex['Alt_bin']*1000,tex['T'])
    ta.plot(tex['T'],tex['Alt_bin'])
    #N2a.plot(N2,tex['Alt_bin'])
    
#for sh in [10,14,22,40]:
#    sda.plot(phi(sh),alts,'k--',alpha=0.3)

Tm = ddf.groupby('Alt_bin')['T'].mean()
Ts = ddf.groupby('Alt_bin')['T'].std()
Tmed = ddf.groupby('Alt_bin')['T'].median()
Tslon = sd_df.groupby('Alt_bin')['T'].mean()

sda.plot(Ts,Ts.index,'k',lw=1)
#sda.plot(Tslon,Tslon.index,'k',lw=2)
ta.errorbar(Tm,Tm.index,xerr=Ts,c='gray',lw=3)
ta.plot(Tmed,Tmed.index,'k',lw=3)


sda.set_ylim(25,90)
sda.set_xlim(0,15)
sda.set_xlabel('Standard Deviation [K]')
sda.set_ylabel('Altitude [km]')

ta.set_ylim(25,90)
ta.set_xlim(140,200)
ta.set_xlabel('Temperature [K]')
ta.set_ylabel('Altitude [km]')

#N2a.set_ylim(25,90)
#N2a.set_xlim(.5e-4,2.e-4)


plt.show()