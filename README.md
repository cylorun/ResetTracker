# **ResetTracker**

## **Setup**

#### Required Mods

 - Atum 1.0.5+
 - SpeedrunIGT 10.7+

#### Settings

 - records path: path to your srigt records file, usually `C:/Users/*user*/speedrunigt/records`
 - break threshold: this is the minimum amount of time needed between resets for the tracker to count that time as break-time, and not towards nph calculations
 - delete-old-records: if this is checked, the tracker will auotmatically delete your record files after they are analyzed
 - autoupdate stats: *not currently in use*
 - vault directory: *not currently in use*
 - twitch username: displayed on the master sheet and will be used in the future to be able to download and analyze your twitch vods
 - latest x sessions: when selecting a session for analysis, you can choose latest x sessions, and this is where you chose how many sessions
 - comparison threshold: your data will be compared to users who have similar target times as you; this variable determines how many seconds other users' target times can deviate from yours
 - use local timezone: determines if session times are in your local timezone or UTC
 - upload anonimity: if this box is checked, your name will not be shown on the master sheet
 - instance count: the number of instances that you run
 - target time: the time that you are going for **in seconds**
 - check all of the last 4 checkboxes that are overworlds that you frequently play

#### Updating

 - you can update versions by running update.exe
 - you can open the github or update through the gui by clicking on the update menu-button

## **Tracking**

#### Start Tracking

 - to start tracking, click the actions menu-button to reveal a dropdown
 - it will prompt you to put a session marker; these session markers are used in analysis, so you can associate certain certain strategies with different session markers to distinguish them in analysis and comparison

#### How It Works

The tracker requires the speedrunigt mod, as it creates records files. These records files provide useful information, including the timeline of the run, information found in the in-game statistics menu, advancements, recipes, and some other things. This tracker stores your stats locally, in the *stats.csv* file. It only stores a run if it has achieved any split, otherwise, it is just added to to the cumulating statistics.

#### Tracked Stats

 - Date and Time: the date and time at which the run ended in UTC
 - Run Type Stats: stats that describe the strategies used in the run
 - Splits: stats that record the time of each split
 - Misc. stats: random stats that aren't really important
 - Cumulating stats: stats that record how many resets and how much time since the last run with a split
 - Session Marker: marks the start of the session and the strategy associated with it

## **Analysis**

#### Splits

#### Entry Breakdown

#### Comparison

## **Credits**
