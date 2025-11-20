### This script creates a meteogram using the Valpo Met Tower data
### Christopher Phillips
### Valparaiso Univ.
### Sept. 13 2024

##### START OPTIONS #####

# Root directory containing data
data_dir = '/archive/campus_mesonet_data/mesonet_data/met_tower/'

# Directory to save the plots
sdir = '/archive/campus_mesonet_data/images'

# Tower longitude
lat0 = 41.46

# Tower timezone (hours from UTC)
tz = -6

# Number of points to use in window averaging (each point is 1 second)
npts = 120

# Font options for the plots
fs = 18
fw = 'bold'

#####  END OPTIONS  #####


### Import required modules
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import matplotlib.pyplot as pp
import numpy as np
import pandas
import pytz

### Helper functions

# Function to do the window averaging
# var, variable to average
def window_ave(var):

    window = np.ones(npts)/npts
    wvar = np.convolve(var, window, mode='valid')

    return wvar

# Function to determine the idealized solar insolation curve
# day, day of year
# wtimes, the plotting times
def solar_curve(day, wtimes):

    # Compute the declination angle of the Earth
    dec_angle = 23.45 * np.sin(np.radians(360 * (284 + day) / 365))

    # Calculate the solar angles
    hour_angles = (wtimes/3600.0-12.0)*15.0
    solar_angles = np.arcsin(
        np.sin(np.radians(lat0))*np.sin(np.radians(dec_angle))+
        np.cos(np.radians(lat0))*np.cos(np.radians(dec_angle))*np.cos(np.radians(hour_angles))
    )
    solar_curve = 1361.0*np.sin(solar_angles)
    solar_curve[solar_angles<=0] = 0.0

    return solar_curve

# Grab the current date (local time)
timezone = pytz.timezone('US/Central')
date = datetime.now(timezone)

# Read the data
data = pandas.read_csv(f'{data_dir}/{date.year}/rapid_ValpoMetTower_{date.strftime("%Y%m%d")}.csv')

# Check if day light savings time
# Logic set this way beause the tower is naturally in DST
if (date > datetime(date.year, 3, 9, tzinfo=timezone)) and (date < datetime(date.year, 11, 2, tzinfo=timezone)):
    dst_value = 1
else:
    dst_value = 0

# Convert dates into times
dates = [datetime.strptime(date, "%Y-%m-%d_%H:%M:%S") for date in data["Server Date (UTC)"].values]
times = np.array([(date-dates[0]).total_seconds() for date in dates], dtype='float')+(dates[0].hour*3600.0+dates[0].minute*60.0+dates[0].second)+dst_value*3600.0+tz*3600.0
#dates = [datetime.strptime(date, "%Y-%m-%d_%H:%M:%S") for date in data["Tower Date (local)"].values]
#times = np.array([(date-dates[0]).total_seconds() for date in dates], dtype='float')+(dates[0].hour*3600.0+dates[0].minute*60.0+dates[0].second)+dst_value*3600.0

# Extract the data from the dataframe and interpolate it to one secondly intervals
itemp = np.interp(np.arange(0, 86400.0+1.0, 1), times, data['Temp (C)'], left=np.nan, right=np.nan)
irh = np.interp(np.arange(0, 86400.0+1.0, 1), times, data['RH (%)'], left=np.nan, right=np.nan)
ipres = np.interp(np.arange(0, 86400.0+1.0, 1), times, data['Pres (mb)'], left=np.nan, right=np.nan)
irain = np.interp(np.arange(0, 86400.0+1.0, 1), times, data['Daily Total Rain (mm)'], left=np.nan, right=np.nan)*0.03937 # mm -> inches
iwspd = np.interp(np.arange(0, 86400.0+1.0, 1), times, data['Wspd (m/s)'], left=np.nan, right=np.nan)
iwdir = np.interp(np.arange(0, 86400.0+1.0, 1), times, data['Wdir (deg)'], left=np.nan, right=np.nan)
isw = np.interp(np.arange(0, 86400.0+1.0, 1), times, data['SWdown (W/m2)'], left=np.nan, right=np.nan)
itimes = np.arange(0, 86400.0+1.0, 1)

# Compute the dewpoint
e = 611.2*np.exp(17.67*itemp/(itemp+243.5))*irh/100.0
Td = -243.5*np.log(e/611.2)/(np.log(e/611.2)-17.67)
TdF = (Td*1.8)+32.0

# Do the window averaging for the other variables
wtemp = window_ave(itemp)
wdewp = window_ave(TdF)
wrh = window_ave(irh)
wpres = window_ave(ipres)
wwspd = window_ave(iwspd)
wwdir = window_ave(iwdir)
wsw = window_ave(isw)
wtimes = window_ave(itimes)

### Make the meteogram
fig, axes = pp.subplots(nrows=4, figsize=(12,14), dpi=600, constrained_layout=True)

# Temperature
wtempF = (wtemp*1.8)+32.0
axes[0].plot(wtimes, wtempF, color='firebrick', label='T')
axes[0].plot(wtimes, wdewp, color='forestgreen', label='Td')
axes[0].plot([0,0],[-100,-100], color='steelblue', label='RH') # Ghost line for RH

try:
    axes[0].set_ylim(np.floor(np.nanmin(wdewp)*0.95), np.ceil(np.nanmax(wtempF)*1.05))
except:
    pass
axes[0].legend(shadow=True, fontsize=14)
axes[0].set_ylabel('Temperature (°F)', fontsize=fs, fontweight=fw)

axes[0].set_title(f'Current Campus Observations - {date.strftime("%b %d, %Y")}\nTwo-minute Average', fontsize=fs, fontweight=fw)

# Relative humidity
axrh = axes[0].twinx()
axrh.plot(wtimes, wrh, color='steelblue')
axrh.set_ylim(0, 105)
axrh.set_yticks([0, 20, 40, 60, 80, 100])
axrh.set_ylabel('Relative humidity (%)', fontsize=fs, fontweight=fw)

# Wind Speed
axes[1].plot(wtimes, wwspd*2.237, color='black', label='Speed')
axes[1].plot([0,0],[-10,-10], color='goldenrod', linestyle=':', label='Direction') # Ghost line for legend

axes[1].set_ylim(0, np.ceil(np.nanmax(wwspd*2.237)*1.05))
axes[1].set_ylabel('Wind Speed (mph)',  fontsize=fs, fontweight=fw)
axes[1].legend(shadow=True, fontsize=14)

# Wind Direction
axdir = axes[1].twinx()
axdir.plot(wtimes, wwdir, color='goldenrod', linestyle=':')

axdir.set_ylim(0, 360)
axdir.set_ylabel('Wind Direction (°)',  fontsize=fs, fontweight=fw)
axdir.set_yticks(np.arange(0,405,45))
axdir.set_yticklabels(['N','NE','E','SE','S','SW','W','NW','N'])

# Pressure
axes[2].plot(wtimes, wpres, color='black', label="Pressure")
axes[2].set_ylabel('Pressure (mb)', fontsize=fs, fontweight=fw)
axes[2].set_ylim(np.floor(np.nanmin(wpres))-5, np.ceil(np.nanmax(wpres)+5))
axes[2].plot([0,0],[-10,-10], color='steelblue', label='Rainfall') # Ghost line for legend
axes[2].legend(shadow=True, fontsize=14)

# Rainfall
axrain = axes[2].twinx()
axrain.plot(itimes[np.isfinite(irain)], irain[np.isfinite(irain)], color='steelblue')
axrain.fill_between(itimes[np.isfinite(irain)], irain[np.isfinite(irain)], color='steelblue')

axrain.set_ylabel('Rainfall (inches)', fontsize=fs, fontweight=fw)
axrain.set_ylim(0, max(1,np.max(irain)+1))

# Solar radiation
axes[3].plot(wtimes, wsw, color='darkgoldenrod', label='Insolation')
ideal_sun = solar_curve((dates[0]-datetime(year=dates[0].year, month=1, day=1)).total_seconds()/86400.0+1, itimes)
axes[3].fill_between(itimes, ideal_sun, color='gold', alpha=0.20)
axes[3].fill_between(itimes, 0, 1, where=ideal_sun<5, color='gray', alpha=0.20, transform=axes[3].get_xaxis_transform())

axes[3].set_ylim(0, np.ceil(np.nanmax(ideal_sun)*1.05))
axes[3].set_ylabel('Solar Insolation (W m$^{-2}$)', fontsize=fs, fontweight=fw)
axes[3].set_xlabel('Time (Local)', fontsize=fs, fontweight=fw)

# Atmospheric transmission
iwsw = np.interp(itimes, wtimes, wsw)
tau = iwsw/ideal_sun
tau[ideal_sun <= 50] = np.nan
axsun = axes[3].twinx()
axsun.plot(itimes, tau, color='black', linestyle='--')
axsun.set_ylim(0.0, 1.0)

axsun.set_ylabel('Transmissivity', fontsize=fs, fontweight=fw)
axes[3].plot([0,0], [-100,-100], color='black', linestyle='--', label="T")
axes[3].legend(shadow=True, fontsize=14)

# Add a grid to everything and handle tick labels
for ax in axes:
    ax.grid()
    ax.set_xlim(0,86400)
    ax.set_xticks(np.arange(0, 93600, 7200))
    ax.set_xticklabels(np.arange(0, 26, 2, dtype=int)%24, fontsize=12)
    ax.tick_params(axis='y', labelsize=14)
axrain.tick_params(axis='y', labelsize=14)
axdir.tick_params(axis='y', labelsize=14)
axrh.tick_params(axis='y', labelsize=14)
axsun.tick_params(axis='y', labelsize=14)

# Save the figure
pp.savefig(f'{sdir}/ValpoMetTower_{date.strftime("%Y%m%d")}.png')
pp.savefig(f'{sdir}/ValpoMetTower_current_obs.png')
pp.close()
