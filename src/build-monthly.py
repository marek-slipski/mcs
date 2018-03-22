#! bin/env/ python
#import sys
import process_raw
import date_input as di
import datetime as dt

###*****only do for months that haven't been created yet

#read in files, convert to single DataFrame
print 'Processing monthly files from'
print str(di.starty)+'/'+str(di.startm).zfill(2)+'/'+str(di.startd).zfill(2)+' to'
print str(di.endy)+'/'+str(di.endm).zfill(2)+'/'+str(di.endd).zfill(2)

tot_months = (di.endy-di.starty)*12+(di.endm-di.startm)+1 #num of loops needed

sdate = dt.datetime(di.starty,di.startm,di.startd) #convert to datetime
svb = 'data/interim/monthly/' #base directory for savefiles

#loop through all months
for monthnum in range(tot_months):
    #find end date of this month
    if sdate.month != 12:
        edate = sdate.replace(month=sdate.month+1)-dt.timedelta(1)
    else:
        edate = sdate.replace(year=sdate.year+1,month=1)-dt.timedelta(1)
    #read in all files for this month
    data, prof_info = process_raw.read_files(
                    sdate.year,sdate.month,sdate.day,edate.year,edate.month,edate.day)

    #Save this month's data to two files...
    save_data = svb+str(sdate.year)+str(sdate.month).zfill(2)+'_ALT.csv'
    save_prof = svb+str(sdate.year)+str(sdate.month).zfill(2)+'_PROF.csv'

    print 'Saving monthly data to'
    print save_data
    print save_prof
    data.to_csv(save_data,index=False) #save data
    prof_info.to_csv(save_prof,index=False) #save profile parameters

    #update to next month
    if sdate.month!=12:
        sdate = sdate.replace(month=sdate.month+1)
    else:
        sdate = sdate.replace(year=sdate.year+1,month=1)
