## MCS
To display and perform some basic actions with Mars Climate Database data.

https://atmos.nmsu.edu/data_and_services/atmospheres_data/MARS/atmosphere_temp_prof.html

### Prerequisites

python packages listed in `requirements.txt`. To install, run:

`pip install -r requirements.txt`

## Download Data
Download raw MCS files using `src/download_files.py`.

## Data
### Get filenames in date range

`python src/findfiles.py YYYYMMDDHH YYYYMMDDHH > files.dat`

### Open as DataFrame
`python src/loadfiles.py files.dat`
