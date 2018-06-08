#!env/bin activate
# Marek Slipski
# 20180604

import argparse

parser = argparse.ArgumentParser('Doit options')
parser.add_argument('dates',nargs=2,
                   help='Start and end dates to search')
#parser.add_argument()

args = parser.parse_args()

filelist = 'filelist.dat'

def task_findfiles():
    return {
        'actions':['python src/findfiles.py '+str(args.dates[0])+' '+str(args.dates[1])+' > '+%(targets)s],
        'targets': [filelist]
    }

def task_splitby():
    return{
        'file_dep': [filelist],
        'actions': ['python src/splitby.py ']
    }