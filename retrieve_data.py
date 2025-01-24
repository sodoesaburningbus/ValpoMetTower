### This script downloads and saves the met_tower data to a file for the day.
### Note: Retrieving computer must be on the tower's local network.
### Christopher Phillips
### Valparaiso University
### Sept. 13th, 2024

### Import libraries
from datetime import datetime
import os
import time
import urllib.request as ureq

### The tower file url
url = 'http://10.3.78.245/twidata.txt'

### location to save the data
sdir = '/archive/campus_mesonet_data/mesonet_data/met_tower'

# Pull the data and process it
data = list(ureq.urlopen(url))
data = list([dat.decode('utf-8') for dat in data]) # Retrieve text file

# Locate data line in test data
for line in data:
    try:
        date = datetime.strptime(line[:17], "%y/%m/%d %H:%M:%S") # Local
        break
    except:
        pass
data = line

wdir = float(data[18:21]) # deg
wspd = float(data[22:27])*0.447 # m/s
sdown = float(data[32:36]) # W/m2
temp = (float(data[45:50])-32.0)/1.8 # 'C
rh = float(data[52:55]) # %
pres = float(data[57:63])*33.86 # hPa
rain = float(data[66:72])*25.4 # mm

# Try to create an annual folder to store the data in
year = date.strftime("%Y")
try:
    os.system(f'mkdir {sdir}/{year}')
except:
    pass

# Save the data
# First try to write to an existing file
try:
    fnout = open(f"{sdir}/{year}/ValpoMetTower_{date.strftime('%Y%m%d')}.csv", 'r+')

    # Check that not saving a duplicate time
    if (datetime.strptime(list(fnout)[-1].split(',')[0], "%Y-%m-%d_%H:%M:%S") == date):
        pass
    else:
         fnout.write(f'\n{date.strftime("%Y-%m-%d_%H:%M:%S")},{temp:.2f},{rh:.2f},{pres:.2f},{rain:.2f},{wspd:.2f},{wdir:.2f},{sdown:.2f}')

except Exception as err: # Must be a new file
    print('WARNING', err)

    fnout = open(f"{sdir}/{year}/ValpoMetTower_{date.strftime('%Y%m%d')}.csv", 'a+')

    # Write header then data
    fnout.write('Date (YYYY-MM-DD_HH:MM:SS local),Temp (C),RH (%),Pres (mb),Rain (mm),Wspd (m/s),Wdir (deg),SWdown (W/m2)')
    fnout.write(f'\n{date.strftime("%Y-%m-%d_%H:%M:%S")},{temp:.2f},{rh:.2f},{pres:.2f},{rain:.2f},{wspd:.2f},{wdir:.2f},{sdown:.2f}')

# Close the file
fnout.close()
