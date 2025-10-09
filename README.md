# ValpoMetTower
This is the code for handling the ValpoMetTower.

rapid_retrieve_data.py - This script runs continuously, polling the tower every second, which is approximately the tower's observation frequency.

retreive_data.py - This script runs once, only pulling the most recent minutely observation.

make_php.py - This script reads in a Tower data file and updates the webpage for the campus current conditions page.

make_plot.py - This script makes a meteogram of the tower data using the minutely observations.

make_rapid_plot.py - This script uses the secondly data to make a meteogram.

run_tower_feed.sh - This bash script handles the rapid_retrieve_data.py program and provides basic start/stop/status functionality.
                    Currently stop functionality is broken and one must use kill -9 manually.
                    Start tower feed with "./run_tower_feed.sh start"

qc_rapid_data.py - This script performs basic quality checks on the 1-secondly observations from the Valpo met tower and is meant to run on a cronjob after retreiving data.
                   First, a 5 minute sliding window is used to remove observations that are 4 standard deviations away from the mean.
                   Then, some filters for missing values and ridiculous observations are applied (e.g. temps greater than 100 'C).
                   Flagged values are then thrown out and interpolated from the surrounding observations.

qc_all_rapid_data.py - Same as qc_rapid_data.py but processes past data.

watchdog.py - Runs on cron to check if data files for the tower are being updated. If not, it restarts the tower feed.


## Example Crontab for running the met tower
```
@reboot /archive/campus_mesonet_data/ValpoMetTower/run_tower_feed.sh start
*/10 * * * * /miniforge3/envs/main/bin/python /archive/campus_mesonet_data/ValpoMetTower/qc_rapid_data.py
*/15 * * * * /miniforge3/envs/main/bin/python /archive/campus_mesonet_data/ValpoMetTower/make_php.py >/dev/null 2>&1
*/15 * * * * /miniforge3/envs/main/bin/python /archive/campus_mesonet_data/ValpoMetTower/make_rapid_plot.py >/dev/null 2>&1
```