from bs4 import BeautifulSoup as BS
import urllib2
import HTMLParser
import requests
import os
import glob
import yaml

from pandas import DataFrame, Series
import pandas as pd
import numpy as np
import datetime as dt


## Get path to data from config file
with open('config.local') as cy:
    config = yaml.load(cy)
path_base = config['data_path']

def download_day_files(year,month,day,datar='DDR'):
    '''
    Download a single Earth-day's worth of MCS data (6 '.TAB' files)
    to a similar volume structure in current directory (see outputs)

    For files, see:
    http://atmos.nmsu.edu/data_and_services/atmospheres_data/MARS/atmosphere_temp_prof.html

    Inputs
    -----
    year, month, day: int, for day of interest
    datar: str, data record of interest {'DDR':derived,'RDR':reduced,'EDR':raw}
    **not verified to work for anything but DDR

    Outputs
    -------
    new files saved as follows:
    ./data/datar/year/yearmonth/yearmonthday/yearmonthday_datar.TAB

    file_count: int, number of files downloaded
    '''

    ###First deal with mrom number
    #Data Record number
    if datar == 'DDR':
        mrom_0 = '2'
    elif datar == 'RDR':
        mrom_0 = '1'
    elif datar == 'EDR':
        mrom_0 = '0'
    #last 3 digits
    mrom_1 = 0 #start at 000
    #001 is September 2006, +1 from there
    if month >= 9:
        mrom_1+= (year-2006)*12+month-8
    else:
        mrom_1+= (year-2007)*12+4+month
    mrom_1 = str(mrom_1).zfill(3) #convert integer to 3 digit string
    mrom = 'MROM_'+mrom_0+mrom_1 #combine with data record

    #Go to URL for single day, download files
    url_base = 'http://atmos.nmsu.edu/PDS/data/'
    year_s = str(year)
    month_s = str(month).zfill(2)
    day_s = str(day).zfill(2)
    dirname = year_s+'/'+year_s+month_s+'/'+year_s+month_s+day_s
    url = url_base+mrom+'/DATA/'+dirname+'/'
    html_req = requests.get(url) #get webpage
    soup= BS(html_req.text,'html.parser') #parse it
    #Find all data links
    urls,names = [],[] #init lists for files
    for i,link in enumerate(soup.find_all('a')): #go through all
        fname = link.get('href')
        full_link = url+fname #full link of file
        if full_link.endswith('.TAB'): #keep data files
            names.append(fname)  #add to lists
            urls.append(full_link)
    unames = zip(names,urls) #to go back through
    #Download each file to similar volume structre
    file_count = 0
    for name, link in unames:
        reqlink = urllib2.Request(link)
        oplink = urllib2.urlopen(reqlink)  #open link
        new_loc = path_base+'/'+mrom[0:6]+'/'+dirname #save location
        if not os.path.exists(new_loc):
            os.makedirs(new_loc) #create directorie if necessary
        new_name = new_loc+'/'+name #attach filename to location
        if not os.path.exists(new_name): #only download new files
            gen_file = open(new_name,'wb') #generate new file
            gen_file.write(oplink.read()) #read data from link
            gen_file.close()
            file_count+=1
    return file_count

def download_files(
    start_year,start_month,start_day,end_year,end_month,end_day,dater='DDR'):
    '''
    Run download_day_files for many days. See that function for more info.

    Inputs
    ------
    start_year/month/day:
    end_year/month/day

    Outputs
    -------
    saved files (see download_day_files)
    file_count: int, number of files downloaded
    '''
    sd = dt.datetime(start_year,start_month,start_day)
    ed = dt.datetime(end_year,end_month,end_day)
    date = dt.datetime(start_year,start_month,start_day)
    file_count = 0 #initialize file count
    while (date >= sd) and (date <= ed): #do for each day
        print date
        file_count += download_day_files(date.year,date.month,date.day)
        date += dt.timedelta(1) #advance to next day
    print 'Number of files downloaded:',file_count
    return file_count

if __name__=='__main__':
    download_files(2016,10,1,2016,10,31)
