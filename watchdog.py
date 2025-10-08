### This script is desgiend to run on a cron schedule.
### It checks the data directory to see if the data is being updated.
### If the data is not being updated, it restarts the data script.
###
### Christopher Phillips
### Valparaiso University

##### START OPTIONS #####

# Root directory containing data
data_dir = '/archive/campus_mesonet_data/mesonet_data/met_tower'

# Threshold for missing data before re-launching job (seconds)
threshold = 1800.0

#####  END OPTIONS  #####
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import os
import pandas
import pytz


# Grab the current date (local time)
#timezone = ZoneInfo('America/Central')
timezone = pytz.timezone('US/Central')
date = datetime.now(timezone)
date_utc = datetime.utcnow()

# Read the data and get the final time
data = pandas.read_csv(f'{data_dir}/{date.year}/rapid_ValpoMetTower_{date.strftime("%Y%m%d")}.csv')
last_date = datetime.strptime(data['Server Date (UTC)'].values[-1], '%Y-%m-%d_%H:%M:%S')

# Check if data if file is updating and re-start job if necessary
if ((date_utc-last_date).total_seconds() >= threshold):
    os.system('run_tower_feed.sh start')
    fn = open('watchdog.log', 'a')
    fn.write('\n Restarted job on {date_utc.strftime("%Y-%m-%d %H%M")} UTC')
    fn.close()