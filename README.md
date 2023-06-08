# ResetTracker

## Setup

#### Required Mods

 - Atum 1.0.5+
 - SpeedrunIGT 10.7+

#### Non-Windows Users

 - Download the source code
 - Make sure you have python and pip installed
 - Open the terminal and set the directory to the `ResetTracker` folder using `cd filepath`
 - Run the program using `python3 gui.py`
 - The program will guide you through the rest of the process

#### Settings

 - Configure your settings in the settings tab and save them. When saving, the program will let you know if you have any invalid values. If you're unsure about the purpose or meaning of a setting, hover over its label for a tooltip to pop up.

#### Updating

If an update is available, the update button on the Control page will be clickable. Pressing it will close the tracker and automatically update it.

#### Sheets

Using sheets is NOT necessary, however if you wish to use google sheets in addition to local storage to store your stats, follow [Talking Mime's Tutorial](https://www.youtube.com/watch?v=KIAo3Lgsk_Q)

## Tracking

#### How It Works

The tracker requires the speedrunigt mod, as it creates records files. These records files provide useful information, including the timeline of the run, information found in the in-game statistics menu, advancements, recipes, and some other things. This tracker stores your stats locally, in the *stats.csv* file. It only stores a run if it has achieved any split, otherwise, it is just added to to the cumulating statistics.

#### Tracked Stats

 - Date and Time: the date and time at which the run ended in UTC
 - Run Type Stats: stats that describe the strategies used in the run
 - Splits: stats that record the time of each split
 - Misc. stats: random stats that aren't used yet but will be used later for research purposes
 - Cumulating stats: stats that record how many resets and how much time since the last run with a split
 - Session Marker: marks the start of the session and the strategy associated with it

## Analysis

IMPORTANT: this tracker is still compatible with specnr's website
Check out each of the pages on the gui; they all do different things. They all have a button that you press to present the analysis, and a description of the page at the top. All graphs and tables have headers above them. If you hover over those headers, a brief explanation of the graph or table may appear. Choose which session you want to be analyzed by clicking on the black drop-down next to the tabs.

## Credits

#### Developers

Original reset tracker was made by TheTalkingMime, and further developed by Specnr. Then I made it better :D. Baryllium did most of the work in making the tracker accessible to mac and linux. Boyenn is also helping me develop the tracker. Also huge thanks to chatGPT for helping me code this!

#### Testers

Huge thanks to those who helped me test, incuding Chloe, Lathil, AeroAsteroid, Ravalle, Boyenn, Priffin, Deuce, and Oceanico.

#### Ideas

Thanks to Weakforced for his countless ideas and help with making decisions and brainstorming solutions

## Suggestions/Help

If you have any suggestions, bug reports, or need help setting it up, DM me on discord pncakespoon#4895 or join [EAR](https://discord.gg/jnjrbysy)

## Features Coming Soon (or Later)

 - More Graphs, data, analysis, and feedback :)
 - Spawn Image Analysis
 - vod runs analysis
 - Comparing stats with your freinds!
 

