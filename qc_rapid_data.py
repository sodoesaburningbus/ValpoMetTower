### This program applies basic quality checks to the
### secondly observations from the Valpo Met Tower.
### A standard deviation check is used to flag suspicious data and interpolate
### from the surrounding observations.
### Does not apply filter to rain due to rain often being a step function.
###
### A QC flag of 1 is good, and -1 is suspicious
###
### Christopher Phillips
### Valparaiso University
### Oct. 2025

##### START OPTIONS #####

# Location of the rapid data files
odir = '/archive/campus_mesonet_data/mesonet_data/met_tower'

# Directory to which to save the quality controlled files
sdir = '/archive/campus_mesonet_data/mesonet_data/met_tower/QCd_data'

# Number of observations to use in standard deviation check (1 s interval)
# Even numbers only!
nobs = 300

# Number of standard deviations for the QC threshold
# e.g. 3 means data more than 3 deviations from the mean over
# the window will be thrown out
nsigma = 0.75

#####  END OPTIONS  #####

# Import required modules
from collections import OrderedDict
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import pytz
import os

# Grab the current date (local time)
#timezone = ZoneInfo('America/Central')
timezone = pytz.timezone('US/Central')
date = datetime.now(timezone)

# Read the data
data_df = pd.read_csv(f'{odir}/{date.year}/rapid_ValpoMetTower_{date.strftime("%Y%m%d")}.csv')

# Convert dates into times
dates = [datetime.strptime(date, "%Y-%m-%d_%H:%M:%S") for date in data_df["Tower Date (local)"].values]
times = np.array([(date-dates[0]).total_seconds() for date in dates], dtype='float')

# Extract data from the data frame
obs = {'temp': data_df['Temp (C)'].values, 'rh': data_df['RH (%)'].values, 'pres': data_df['Pres (mb)'].values,
       'rain': data_df['Daily Total Rain (mm)'].values, 'wspd': data_df['Wspd (m/s)'].values, 'wdir': data_df['Wdir (deg)'].values,
       'swdown': data_df['SWdown (W/m2)'].values}

# Compute the standard deviation for each point and flag suspicious data
# Then replace data and interpolate to uniform one second interval
flags = {} # QC flags
iobs = {} # Final interpolated data
for k in obs.keys():
    # Array to hold the QC flags
    flags[k] = np.ones(obs[k].size)

    # Compute mean and standard deviation over the window
    for i in range(obs[k].size):
        if (i < nobs//2): # left edge
            sigma = np.nanstd(obs[k][i-nobs//2+(nobs//2-i):i+nobs//2]+(nobs//2-i))
            mean = np.nanmean(obs[k][i-nobs//2+(nobs//2-i):i+nobs//2+(nobs//2-i)])

        elif (obs[k].size-i < nobs//2): # right edge
            sigma = np.nanstd(obs[k][i-nobs//2-(nobs//2-i):i-nobs//2]+(nobs//2-i))
            mean = np.nanmean(obs[k][i-nobs//2-(nobs//2-i):i-nobs//2+(nobs//2-i)])

        else: # body
            sigma = np.nanstd(obs[k][i-nobs//2:i+nobs//2])
            mean = np.nanmean(obs[k][i-nobs//2:i+nobs//2])

        # Apply the sigma filter
        if (abs(obs[k][i]-mean)>nsigma*sigma):
            flags[k][i] = -1

        # Check for -999
            if (obs[k][i] == -999):
                flags[k][i] = -1

        # Apply some other basic filters
        if (k == 'temp') and (obs[k][i] > 100):
            flags[k][i] = -1
        elif (k == 'rh') and (obs[k][i] > 105):
            flags[k][i] = -1
        elif (k == 'pres') and (obs[k][i] < 940):
            flags[k][i] = -1

    # If rain, just set all flags to good because it IS often a step function
    if (k == 'rain'):
        flags[k] = np.ones(obs[k].size)

    # Interpolate the suspicious data
    obs[k][flags[k] == -1] = np.nan
    obs[k][np.isnan(obs[k])] = np.interp(times[np.isnan(obs[k])], times[~np.isnan(obs[k])], obs[k][~np.isnan(obs[k])], left=np.nan, right=np.nan)

    # Extend QC flags to any remaining NaNs
    flags[k][np.isnan(obs[k])] == -1

# Final dictionary for writing out
out_dict = OrderedDict([
    ('Server Date (UTC)', data_df['Server Date (UTC)'].values),
    ('Tower Date (local)', data_df["Tower Date (local)"].values),
    ('Temp (C)', obs['temp']), ('Temp QC', flags['temp']),
    ('RH (%)', obs['rh']), ('RH QC', flags['rh']),
    ('Pres (mb)', obs['pres']), ('Pres QC', flags['pres']),
    ('Daily Total Rain (mm)', obs['rain']), ('Rain QC', flags['rain']),
    ('Wspd (m/s)', obs['wspd']), ('Wspd QC', flags['wspd']),
    ('Wdir (deg)', obs['wdir']), ('Wdir QC', flags['wdir']),
    ('SWdown (W/m2)', obs['swdown']), ('SWdown QC', flags['swdown'])
])

# Convert to dictionary and replace any empty strings with NaNs
out_df = pd.DataFrame(out_dict)
out_df = out_df.replace(r'^\s*$', np.nan, regex=True)

# Write out the QC'd file
try:
    os.system(f'mkdir -p {sdir}/{date.year}')
except:
    pass

out_df.to_csv(f'{sdir}/{date.year}/rapid_qc_ValpoMetTower_{date.strftime("%Y%m%d")}.csv', float_format='%.2f', index=False)
