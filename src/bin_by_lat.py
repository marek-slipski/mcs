#! env/bin python

import glob
altfiles= glob.glob('../data/interim/monthly/*_ALT.csv')
proffiles= glob.glob('../data/interim/monthly/*_PROF.csv')

##call some other function that defines latitude bins....

#this script will loop through monthly data and
#bin each month by latitude. The general altiude binning
#and subsequent averaging should work for any already binned data
def monthly_lat_bins(latbins):
    '''
    Inputs
    ------
    latbins: array, latitude bins given, each bin is [n, n+1]

    Outputs
    -------
     DataFrames for each latitude bin for each month?
    '''
    for filenum, datafile in enumerate(altfiles):
        print '\nReading in data from ',datafile
        data = pd.read_csv(datafile)
        prof = pd.read_csv(proffiles[filenum])
        latcut = pd.cut(prof['Profile_lat'],latbins)
        latdata = []
        latnames = []
