### This script adjusts the website page for Valpo's current weather
### Christopher Phillips
### Valpo Univ. Sept. 20th, 2024

##### START OPTIONS #####

# Location of php template
template = '/var/www/html/current/index_template.php'

# Location to save new file
spath = '/var/www/html/current/index.php'

# Root directory containing data
data_dir = '/archive/campus_mesonet_data/mesonet_data/met_tower'

#####  END OPTIONS  #####

# Import modules
from datetime import datetime, timedelta
import numpy as np
import pandas
from zoneinfo import ZoneInfo

# Grab the current date (local time)
timezone = ZoneInfo('America/Chicago')
date1 = datetime.now(timezone)
date2 = date1-timedelta(days=1)

# Read the data
data1 = pandas.read_csv(f'{data_dir}/{date1.year}/rapid_ValpoMetTower_{date1.strftime("%Y%m%d")}.csv')
data2 = pandas.read_csv(f'{data_dir}/{date2.year}/rapid_ValpoMetTower_{date2.strftime("%Y%m%d")}.csv')

# Find the extremes
Tmax1 = np.nanmax(data1['Temp (C)'])*1.8+32.0
Tmin1 = np.nanmin(data1['Temp (C)'])*1.8+32.0
Wind1 = np.nanmax(data1['Wspd (m/s)'])*2.237
rain1 = np.nanmax(data1['Rain (mm)'])*0.03937

Tmax2 = np.nanmax(data2['Temp (C)'])*1.8+32.0
Tmin2 = np.nanmin(data2['Temp (C)'])*1.8+32.0
Wind2 = np.nanmax(data2['Wspd (m/s)'])*2.237
rain2 = np.nanmax(data2['Rain (mm)'])*0.03937

# Get the latest data
T0 = data1['Temp (C)'].values[-1]*1.8+32.0
Wspd0 = data1['Wspd (m/s)'].values[-1]*2.237
Wdir0 = data1['Wdir (deg)'].values[-1]
sw0 = data1['SWdown (W/m2)'].values[-1]
RH0 = data1['RH (%)'].values[-1]
P0 = data1['Pres (mb)'].values[-1]

# Open the template and the new file
fn_in = open(template, 'r')
fn_out = open(spath, 'w')

# Loop over template
first = True
for line in fn_in:

    if ("High Temperature" in line):
        if first:
            newline = f"          <p>High Temperature: {Tmax1:.1f} °F<br>Low Temperature: {Tmin1:.1f} °F<br>Wind Gust: {Wind1:.1f} mph<br>Rainfall: {rain1:.2f} inches</p>\n"
            fn_out.write(newline)
            first = False
        else:
            newline = f"          <p>High Temperature: {Tmax2:.1f} °F<br>Low Temperature: {Tmin2:.1f} °F<br>Wind Gust: {Wind2:.1f} mph<br>Rainfall: {rain2:.2f} inches</p>\n"
            fn_out.write(newline)

    elif ("Insolation" in line):
        newline = f"          <p>Temperature: {T0:.1f} °F<br>Rel. Humidity: {RH0:.0f}%<br>Wind Speed: {Wspd0:.1f} mph<br>Wind Direction: {Wdir0:.0f}°<br>Pressure: {P0:.1f} mb<br>Rainfall: {rain1:.2f} inches<br>Insolation: {sw0:.1f} W m<sup>-2</sup></p>\n"
        fn_out.write(newline)

    else:
        fn_out.write(line)

fn_out.close()
fn_in.close()
