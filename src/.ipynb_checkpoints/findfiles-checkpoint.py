import yaml
import datetime as dt

## Get path to data from config file
with open('src/config.yaml') as cy:
    config = yaml.load(cy)
path_base = config['data_path']

def str_dt(date_st):
    '''
    Convert str to datetime object
    '''
    if len(date_st) == 10:
        date_dt = dt.datetime.strptime(date_st,'%Y%m%d%H')
    elif len(date_st) == 8:
        date_dt = dt.datetime.strptime(date_st,'%Y%m%d')
    elif len(date_st) == 6:
        date_dt = dt.datetime.strptime(date_str,'%Y%m')
    elif len(date_st) == 4:
        date_dt = dt.datetime.strptime(date_str,'%Y')
    return date_dt

def file_from_date(file_dt):
    '''
    Given a datetime object with year, month, day, and hour
    get path to desired file
    
    Inputs
    ------
    file_dt: datetime object, 6 files per day
    
    Outputs
    -------
    path_file: str, path to desired files
    '''
    path_date = ''
    for ddir in ['%Y','%Y%m','%Y%m%d','%Y%m%d%H']:
        path_date += '/'+file_dt.strftime(ddir)
    #path_file = path_base + path_date + '_DDR.TAB'
    path_file = path_date + '_DDR.TAB'
    return path_file

def files_drange(start,end):
    '''
    Return list of file names between start date and end date
    Input
    -----
    start,end: str, start and end dates to parse
    
    Outputs
    ------
    files: list, paths to files between start and end
    '''
    new_dt = str_dt(start) #get dt objects of strings
    end_dt = str_dt(end)
    if new_dt.hour %4 != 0: # files have to be in 4-hour intervals
        new_dt = new_dt.replace(hour = 4*divmod(new_dt.hour,4)[0]) #change hour
    files = [] #initialize
    while new_dt < end_dt: #loop between
        new_file = file_from_date(new_dt) #get file path
        files.append(new_file) # add to list
        new_dt = new_dt + dt.timedelta(hours=4) #update datetime
    return files

if __name__ == '__main__':
    import sys
    start = sys.argv[1]
    if len(sys.argv) > 2:
        end = sys.argv[2]
    else:
        end = str(int(start) + 1)
    
    files = files_drange(start,end)
    
    for f in files:
        print f