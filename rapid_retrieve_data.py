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
import xml.etree.ElementTree as ET

### The tower file url
url = 'http://10.3.78.245/status.xml'

### location to save the data
sdir = '/archive/campus_mesonet_data/mesonet_data/met_tower'

while True:

    # Pull the data and process it
    server_time = datetime.utcnow()
    data = list(ureq.urlopen(url))
    data = list([dat.decode('utf-8') for dat in data]) # Retrieve text file
    root = ET.fromstring(''.join(data))

    wdir = float(root[4].text) # deg
    wspd = float(root[5].text)*0.447 # m/s
    sdown = float(root[6].text) # W/m2
    temp = (float(root[10].text)-32.0)/1.8 # 'C
    rh = float(root[11].text) # %
    pres = float(root[12].text)*33.86 # hPa
    rain = float(root[16].text)*25.4 # mm
    day_rain = float(root[14].text)*25.4 # mm
    date = datetime.strptime(root[2].text+root[1].text, "%m/%d/%y%H:%M:%S")

    # Try to create an annual folder to store the data in
    year = date.strftime("%Y")
    try:
        os.system(f'mkdir {sdir}/{year} > /dev/null 2>&1')
    except:
        pass

    # Save the data
    # First try to write to an existing file
    try:
        fnout = open(f"{sdir}/{year}/rapid_ValpoMetTower_{date.strftime('%Y%m%d')}.csv", 'r+')

        # Check that not saving a duplicate time
        if (datetime.strptime(list(fnout)[-1].split(',')[0], "%Y-%m-%d_%H:%M:%S") == date):
            pass
        else:
            fnout.write(f'\n{server_time.strftime("%Y-%m-%d_%H:%M:%S")},{date.strftime("%Y-%m-%d_%H:%M:%S")},{temp:.2f},{rh:.2f},{pres:.2f},{rain:.2f},{day_rain:.2f},{wspd:.2f},{wdir:.2f},{sdown:.2f}')

    except Exception as err: # Must be a new file
        print('WARNING', err)

        fnout = open(f"{sdir}/{year}/rapid_ValpoMetTower_{date.strftime('%Y%m%d')}.csv", 'a+')

        # Write header then data
        fnout.write('Server Date (UTC),Tower Date (local),Temp (C),RH (%),Pres (mb),Rain Rate (mm),Daily Total Rain (mm),Wspd (m/s),Wdir (deg),SWdown (W/m2)')
        fnout.write(f'\n{server_time.strftime("%Y-%m-%d_%H:%M:%S")},{date.strftime("%Y-%m-%d_%H:%M:%S")},{temp:.2f},{rh:.2f},{pres:.2f},{rain:.2f},{day_rain:.2f},{wspd:.2f},{wdir:.2f},{sdown:.2f}')

    # Close the file
    fnout.close()

    # Delay 1 second
    time.sleep(1)
