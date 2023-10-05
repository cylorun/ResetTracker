# ResetTracker

## Setup

#### Required Mods

 - Atum 1.0.5+
 - SpeedrunIGT 10.7+

#### Sheets (Converting from Old Tracker)

Instead of repeating the google sheets setup:
 - Duplicate the `Raw Data` subsheet 
 - Rename the duplicate to `Archive` and clear the data in the original subsheet
 - Move your `credentials.json` from the old tracker's folder to the new tracker's folder

#### Sheets (New Users)

 - Follow [Talking Mime's Tutorial](https://www.youtube.com/watch?v=KIAo3Lgsk_Q) to create credentials.json (0:01 - 1:41)
 - Make a copy of an existing spreadsheet and clear its data, or use the [template](https://docs.google.com/spreadsheets/d/1XvRLLQ5J1zAqraUkJ06qAGdYTeCFHhnmrv2nkWoXIO0/edit#gid=1357582403)
 - Share your google sheet with the service account and give it editing permissions

#### Windows Users
 - after downloading the latest release, unzip it and launch `ResetTracker2.exe`
 - The program will guide you through the rest of the process

#### Non-Windows Users

 - Download the source code
 - Make sure you have python and pip installed
 - Open the terminal and set the directory to the `ResetTracker2` folder using `cd filepath`
 - Run the program using `python3 tracker.py`
 - The program will guide you through the rest of the process

## Updating
update.exe has not been confirmed stable yet. For now, just manually update.

## Viewing your stats

#### Website

 - The [Reset Analytics Website](https://reset-analytics.vercel.app), developed by Specnr, Boyenn, and myself, is how you will access detailed analysis of your stats
 - It will not work if your spreadsheet isn't publicly viewable, or if there is no data on the spreadsheet
 - The [Github Repo](https://github.com/Specnr/ResetAnalytics) has additional information

#### Discord Bot

 - You can also invite the [Discord Bot](https://discord.com/oauth2/authorize?client_id=1151605577265451128&scope=bot&permissions=274877910016) to your server
 - More info is available on the [Github Repo](https://github.com/pncakespoon1/MCSRstatbot)



## Tracking

#### How It Works

The tracker requires the speedrunigt mod, as it creates records files. These records files provide useful information, including the timeline of the run, information found in the in-game statistics menu, advancements, recipes, and some other things. It only stores a run if it has achieved any split, otherwise, it is just added to to the cumulating statistics.

#### Tracked Stats

 - Date and Time: the date and time at which the run ended in UTC
 - Run Type Stats: stats that describe the strategies used in the run
 - Splits: stats that record the time of each split
 - Misc. stats: random stats that aren't used yet but will be used later for research purposes
 - Cumulating stats: stats that record how many resets and how much time since the last run with a split
 - Session Marker: marks the start of the session and the strategy associated with it

## Credits

#### Developers

Original reset tracker was made by TheTalkingMime, and further developed by Specnr. Then I made it better :D. Baryllium did most of the work in making the tracker accessible to mac and linux. Boyenn also helped with various parts of the code. Also huge thanks to chatGPT for helping me code this!

#### Testers

Huge thanks to those who helped me test the program early on, incuding Chloe, Lathil, AeroAsteroid, Ravalle, Boyenn, Priffin, Deuce, and Oceanico.

#### Ideas

Thanks to Weakforced for his countless ideas and help with making decisions and brainstorming solutions

## Suggestions/Help

If you have any suggestions, bug reports, or need help setting it up, DM me on discord pncakespoon#4895 or join [EAR](https://discord.gg/jnjrbysy)
 

