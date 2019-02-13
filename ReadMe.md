## MCS
Explore MCS temperature profiles.
Perform some basic actions and display plots with Mars Climate Sounder L2 data.

https://atmos.nmsu.edu/data_and_services/atmospheres_data/MARS/atmosphere_temp_prof.html

### Prerequisites
python packages listed in `requirements.txt`. To install, run:

`pip install -r requirements.txt`

## Data
### Download
First, copy config.template to config.local and setup desired paths.
To download MCS L2 files, use `src/download_files.py`. Downloads them to path set by config.local.

### Get filenames in date range
To work with data, first select the files to be used by a range of dates.
`python src/findfiles.py YYYYMMDDHH YYYYMMDDHH > files.dat`

### Split by latitude, local time, Ls, or longitude
From a list of filenames output from `src/findfiles.py` get profiles from a given time or location.
Generates DataFrame that can be saved as csv.
`python src/splitby.py files.dat > profiles.dat` Use `-h` for more options.

### Plot map of observations
View map of profiles (local time vs. latitude)
`python src/map_profiles.py files.dat`

### Plot temperature profiles
Temp vs. altitude plots.
`python src/temp_profiles.py files.dat profiles.dat` or
`python src/temp_profiles.py data.csv meta.csv`

### Temperature vs. Altitude/Pressure contours
Plot temperatures as a function of altitude and latitude, longitude, local time, or Ls
`python src/long_plots.py files.dat profiles.dat` or
`python src/long_plots.py data.csv meta.csv`
