import pygsheets
import glob
import os
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
import requests
import webbrowser
import subprocess
import sys

from guiUtils import *


"""
global variables
"""

if True:
    databaseLink = "https://docs.google.com/spreadsheets/d/1ky0mgYjsDE14xccw6JjmsKPrEIDHpt4TFnD2vr4Qmcc"
    headerLabels = ['Date and Time', 'Iron Source', 'Enter Type', 'Gold Source', 'Spawn Biome', 'RTA', 'Wood', 'Iron Pickaxe', 'Nether', 'Bastion', 'Fortress', 'Nether Exit', 'Stronghold', 'End', 'Retimed IGT', 'IGT', 'Gold Dropped', 'Blaze Rods', 'Blazes', 'Flint', 'Gravel', 'Deaths', 'Traded', 'Endermen', 'Eyes Thrown', 'Iron', 'Wall Resets Since Prev', 'Played Since Prev', 'RTA Since Prev', 'Break RTA Since Prev', 'Wall Time Since Prev', 'Session Marker', 'RTA Distribution']
    config = FileLoader.getConfig()
    settings = FileLoader.getSettings()
    sessions = FileLoader.getSessions()
    thresholds = FileLoader.getThresholds()
    wks1 = -1
    if getattr(sys, 'frozen', False):  # if running in a PyInstaller bundle
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    gc_sheets_database = pygsheets.authorize(service_file=os.path.join(base_path, 'databaseCredentials.json'))
    sh2 = gc_sheets_database.open_by_url(databaseLink)
    wks2 = sh2[0]
    second = timedelta(seconds=1)
    currentSession = {'splits stats': {}, 'general stats': {}}
    currentSessionMarker = 'X'
    selectedSession = None
    isTracking = False
    isUpdating = False
    isGraphingGeneral = False
    isGraphingSplit = False
    isGraphingEntry = False
    isGraphingComparison = False
    isGivingFeedback = False
    updateStatsLoadingProgress = ''
    advChecks = [
        ("minecraft:recipes/misc/charcoal", "has_log"),
        ("minecraft:story/iron_tools", "iron_pickaxe"),
        ("timelines", "enter_nether"),
        ("timelines", "enter_bastion"),
        ("timelines", "enter_fortress"),
        ("timelines", "nether_travel"),
        ("timelines", "enter_stronghold"),
        ("timelines", "enter_end"),
    ]

    statsChecks = [
        "nothing lol",
        ("minecraft:dropped", "minecraft:gold_ingot"),
        ("minecraft:picked_up", "minecraft:blaze_rod"),
        ("minecraft:killed", "minecraft:blaze"),
        ("minecraft:picked_up", "minecraft:flint"),
        ("minecraft:mined", "minecraft:gravel"),
        ("minecraft:custom", "minecraft:deaths"),
        ("minecraft:custom", "minecraft:traded_with_villager"),
        ("minecraft:killed", "minecraft:enderman"),
        ("minecraft:picked_up", "minecraft:ender_eye")
    ]

"""
global variables
"""


class Update:
    @classmethod
    def checkGithub(cls):
        latest = requests.get("https://api.github.com/repos/pncakespoon1/ResetTracker/releases/latest")
        if latest == config['version']:
            return False
        else:
            return True

    @classmethod
    def update(cls):
        subprocess.Popen('update.exe')
        root.destroy()


    @classmethod
    def openGithub(cls):
        webbrowser.open_new_tab('https://github.com/pncakespoon1/ResetTracker')


class Database:

    @classmethod
    def uploadData(cls):
        global config
        careerData = Stats.getSessionData("All", sessions)
        nameList = (wks2.get_col(col=1, returnas='matrix', include_tailing_empty=False))
        userCount = len(nameList)
        if config['lbName'] == '':
            if settings['display']['upload anonymity'] == 1:
                config['lbName'] = "Anonymous" + str(userCount).zfill(5)
            else:
                config['lbName'] = settings['display']['twitch username']
            configFile = open('data/config.json')
            json.dump(config, configFile)
            configFile.close()
        values = [config['lbName'], str(int(settings['playstyle']['instance count'])), str(int(settings['playstyle']['target time']))]
        for statistic in ['rnph', 'rpe', 'percent played', 'efficiency score']:
            values.append(careerData['general stats'][statistic])
        for statistic in ['Cumulative Average', 'Relative Average', 'Relative Conversion', 'xph']:
            for split in ['Iron', 'Wood', 'Iron Pickaxe', 'Nether', 'Structure 1', 'Structure 2', 'Nether Exit', 'Stronghold', 'End']:
                values.append(careerData['splits stats'][split][statistic])
        if config['lbName'] in nameList:
            rownum = nameList.index(config['lbName']) + 1
            wks2.update_row(index=rownum - 1, values=values, col_offset=0)
        else:
            wks2.insert_rows(row=userCount, number=1, values=values, inherit=False)


class CurrentSession:
    @classmethod
    def updateCurrentSession(cls, row):
        global currentSession
        rowCells = {}
        for i in range(len(headerLabels)):
            if row[i] is not None and '-' in row[i] and ':' in row[i]:
                rowCells[headerLabels[i]] = row[i]
            elif row[i] is not None and ':' in row[i]:
                rowCells[headerLabels[i]] = Logistics.stringToTimedelta(row[i])/second
            elif type(row[i]) == str:
                try:
                    rowCells[headerLabels[i]] = int(row[i])
                except Exception as e2:
                    rowCells[headerLabels[i]] = row[i]
            else:
                rowCells[headerLabels[i]] = row[i]

        # resets/time
        currentSession['general stats']['total RTA'] += rowCells['RTA'] + rowCells['RTA Since Prev']
        currentSession['general stats']['total wall resets'] += int(rowCells['Wall Resets Since Prev'])
        currentSession['general stats']['total played'] += int(rowCells['Played Since Prev']) + 1
        currentSession['general stats']['total wall time'] += int(rowCells['Wall Time Since Prev'])

        # overworld
        for split in ['Wood', 'Iron Pickaxe', 'Iron']:
            if rowCells[split] is not None:
                currentSession['splits stats'][split]['Cumulative Sum'] += rowCells[split]
                currentSession['splits stats'][split]['Relative Sum'] += rowCells[split]
                currentSession['splits stats'][split]['Count'] += 1

        # nether
        if rowCells['Nether'] is not None:
            currentSession['splits stats']['Nether']['Cumulative Sum'] += rowCells['Nether']
            currentSession['splits stats']['Nether']['Relative Sum'] += rowCells['Nether']
            currentSession['splits stats']['Nether']['Count'] += 1
            currentSession['general stats']['total ow time'] += rowCells['Nether'] + rowCells['RTA Since Prev']

            bast = (rowCells['Bastion'] is not None)
            fort = (rowCells['Fortress'] is not None)

            if fort and bast:
                fortFirst = (rowCells['Bastion'] > rowCells['Fortress'])
                st1 = 'Bastion'
                st2 = 'Fortress'
                if fortFirst:
                    st1 = 'Fortress'
                    st2 = 'Bastion'
                currentSession['splits stats']['Structure 1']['Cumulative Sum'] += rowCells[st1]
                currentSession['splits stats']['Structure 1']['Relative Sum'] += rowCells[st1] - rowCells['Nether']
                currentSession['splits stats']['Structure 1']['Count'] += 1
                currentSession['splits stats']['Structure 2']['Cumulative Sum'] += rowCells[st2]
                currentSession['splits stats']['Structure 2']['Relative Sum'] += rowCells[st2] - rowCells[st1]
                currentSession['splits stats']['Structure 2']['Count'] += 1

                if rowCells['Nether Exit'] is not None:
                    currentSession['splits stats']['Nether Exit']['Cumulative Sum'] += rowCells['Nether Exit']
                    currentSession['splits stats']['Nether Exit']['Relative Sum'] += rowCells['Nether Exit'] - rowCells[st2]
                    currentSession['splits stats']['Nether Exit']['Count'] += 1
                    if rowCells['Stronghold'] is not None:
                        currentSession['splits stats']['Stronghold']['Cumulative Sum'] += rowCells['Stronghold']
                        currentSession['splits stats']['Stronghold']['Relative Sum'] += rowCells['Stronghold'] - rowCells['Nether Exit']
                        currentSession['splits stats']['Stronghold']['Count'] += 1
                        if rowCells['End'] is not None:
                            currentSession['splits stats']['End']['Cumulative Sum'] += rowCells['End']
                            currentSession['splits stats']['End']['Relative Sum'] += rowCells['End'] - rowCells['Stronghold']
                            currentSession['splits stats']['End']['Count'] += 1
            elif bast:
                currentSession['splits stats']['Structure 1']['Cumulative Sum'] += rowCells['Bastion']
                currentSession['splits stats']['Structure 1']['Relative Sum'] += rowCells['Bastion'] - rowCells['Nether']
                currentSession['splits stats']['Structure 1']['Count'] += 1
            elif fort:
                currentSession['splits stats']['Structure 1']['Cumulative Sum'] += rowCells['Fortress']
                currentSession['splits stats']['Structure 1']['Relative Sum'] += rowCells['Fortress'] - rowCells['Nether']
                currentSession['splits stats']['Structure 1']['Count'] += 1
        else:
            currentSession['general stats']['total ow time'] += rowCells['RTA'] + rowCells['RTA Since Prev']

        # calculate and update other statistics
        prevSplit = None
        for split in ['Iron', 'Wood', 'Iron Pickaxe', 'Nether', 'Structure 1', 'Structure 2', 'Nether Exit', 'Stronghold', 'End']:
            currentSession['splits stats'][split]['Cumulative Average'] = Logistics.getQuotient(currentSession['splits stats'][split]['Cumulative Sum'], currentSession['splits stats'][split]['Count'])
            currentSession['splits stats'][split]['Relative Average'] = Logistics.getQuotient(currentSession['splits stats'][split]['Relative Sum'], currentSession['splits stats'][split]['Count'])
            currentSession['splits stats'][split]['Cumulative Conversion'] = Logistics.getQuotient((currentSession['splits stats'][split]['Count']), currentSession['general stats']['total played'])
            if prevSplit is not None:
                currentSession['splits stats'][split]['Relative Conversion'] = Logistics.getQuotient(currentSession['splits stats'][split]['Count'], currentSession['splits stats'][prevSplit]['Count'])
            else:
                currentSession['splits stats'][split]['Relative Conversion'] = currentSession['splits stats'][split]['Cumulative Conversion']
            if split not in ['Iron', 'Wood', 'Iron Pickaxe']:
                prevSplit = split

        currentSession['general stats']['rnph'] = Logistics.getQuotient(Logistics.getQuotient(currentSession['splits stats']['Nether']['Count'], currentSession['general stats']['total wall time'] + currentSession['general stats']['total ow time']), 1/3600)
        currentSession['general stats']['% played'] = Logistics.getQuotient(currentSession['general stats']['total played'], currentSession['general stats']['total played'] + currentSession['general stats']['total wall resets'])
        currentSession['general stats']['rpe'] = Logistics.getQuotient(currentSession['general stats']['total wall resets'] + currentSession['general stats']['total played'], currentSession['splits stats']['Nether']['Count'])

        try:
            currentSession['figs'][0] = Graphs.graph6(currentSession)
        except Exception as e:
            pass
        try:
            currentSession['figs'][1] = Graphs.graph7(currentSession)
        except Exception as e:
            pass

        main1.updateCSGraphs()
        CurrentSession.updateObsTxts()


    @classmethod
    def resetCurrentSession(cls):
        global currentSession
        currentSession = {'splits stats': {}, 'general stats': {}, 'figs': [None, None]}
        for split in ['Iron', 'Wood', 'Iron Pickaxe', 'Nether', 'Structure 1', 'Structure 2', 'Nether Exit', 'Stronghold', 'End']:
            currentSession['splits stats'][split] = {'Count': 0, 'Cumulative Sum': 0, 'Relative Sum': 0, 'Cumulative Average': None, 'Relative Average': None, 'Cumulative Conversion': None, 'Relative Conversion': None}
        currentSession['general stats'] = {'total RTA': 0, 'total wall resets': 0, 'total played': 0, 'total wall time': 0, 'total ow time': 0, 'rnph': None, '% played': None, 'rpe': None}

    @classmethod
    def updateObsTxts(cls):
        statDict = {'NPH': Logistics.formatValue(currentSession['general stats']['rnph']),
                    'EnterAvg': Logistics.formatValue(currentSession['splits stats']['Nether']['Cumulative Average'],
                                                      isTime=True),
                    'EnterCount': Logistics.formatValue(currentSession['splits stats']['Nether']['Count'])}
        if not os.path.exists('obs'):
            os.mkdir('obs')
            for stat in statDict.keys():
                txtFile = open('obs/' + stat+ '.txt', 'x')
                txtFile.close()
        for stat in statDict.keys():
            with open('obs/' + stat + '.txt', 'w') as obsTxtFile:
                obsTxtFile.write(statDict[stat])
                obsTxtFile.close()


# class methods for giving feedback
class Feedback:
    @classmethod
    def splits(cls, split, average, formulaDict):
        try:
            targetTime = int(settings['playstyle']['target time'])
        except Exception as e:
            main1.errorPoppup("target time must be in seconds as an integer")
            return None
        return Logistics.getResidual(average, formulaDict[split]['m'], targetTime, formulaDict[split]['b'])

    @classmethod
    def splitsA(cls, split, average):
        formulaDict = thresholds['splitFormulas']
        return Feedback.splits(split, average, formulaDict)


    @classmethod
    def readDatabase(cls):
        targetTimeCol = wks2.get_col(col=3, returnas='matrix', include_tailing_empty=False)
        targetTimeCol.pop(0)
        similarUserList = []
        for i in range(len(targetTimeCol)):
            if -1 * int(settings['display']['comparison threshold']) < (
                    int(targetTimeCol[i]) - int(settings['playstyle']['target time'])) < int(
                    settings['display']['comparison threshold']):
                row = wks2.get_row(row=i, returnas='matrix', include_tailing_empty=True)
                similarUserList.append(row)
        return similarUserList

    @classmethod
    def splitDataPercentiles(cls, data):
        splits = ['Iron', 'Wood', 'Iron Pickaxe', 'Nether', 'Structure 1', 'Structure 2', 'Nether Exit', 'Stronghold', 'End']
        similarUserList = Feedback.readDatabase()
        myData = [[], [], []]
        for i in range(9):
            myData[0].append(data['splits stats'][splits[i]]['Cumulative Average'])
            myData[1].append(data['splits stats'][splits[i]]['Relative Average'])
            myData[2].append(data['splits stats'][splits[i]]['Relative Conversion'])
        myData = myData[0] + myData[1] + myData[2]

        splitLists = np.transpose(np.array(similarUserList))
        splitLists = splitLists[7:]
        percentiles = {}
        for i in range(len(splitLists)):
            if i < 9:
                percentiles[splits[i % 9]] = {}
                percentiles[splits[i % 9]]["cAverage"] = Logistics.get_percentile(Logistics.floatList(splitLists[i]), myData[i])
            elif i < 18:
                percentiles[splits[i % 9]]["rAverage"] = Logistics.get_percentile(Logistics.floatList(splitLists[i]), myData[i])
            elif i < 27:
                percentiles[splits[i % 9]]["Conversion"] = Logistics.get_percentile(Logistics.floatList(splitLists[i]), myData[i])
            elif i < 36:
                percentiles[splits[i % 9]]["xph"] = Logistics.get_percentile(Logistics.floatList(splitLists[i]), myData[i])
        return percentiles

    @classmethod
    def getZfromLinReg(cls, x_index, y_index):
        myData, similarUserList = Feedback.readDatabase()
        similarUserList = np.transpose(np.array(similarUserList))
        targetTimeList = similarUserList[x_index]
        scoreList = similarUserList[y_index]
        myTargetTime = myData[x_index]
        myScore = myData[y_index]
        reg_m, reg_b, reg_s = Logistics.getRegressionLine(targetTimeList, scoreList)
        return (myScore - (reg_m * myTargetTime + reg_b))/reg_s

    @classmethod
    def percentilesToText(cls, percentiles, differenceThreshold):
        problematicSplits = []
        textDict = {'Structure 1': 'before entering the bastion', 'Structure 2': 'from bastion enter to fort enter', 'Nether Exit': 'in the fort', 'Stronghold': 'after exiting the nether'}
        text = ''

        for key in percentiles.keys():
            if key in textDict.keys():
                if percentiles[key]['Conversion'] > 0.5 + differenceThreshold and percentiles[key]['rAverage'] > 0.5 + differenceThreshold:
                    problematicSplits.append({'split': key, 'problem': 1})
                elif percentiles[key]['Conversion'] < 0.5 - differenceThreshold and percentiles[key]['rAverage'] < 0.5 - differenceThreshold:
                    problematicSplits.append({'split': key, 'problem': 2})
                elif percentiles[key]['Conversion'] > 0.5 + differenceThreshold and percentiles[key]['rAverage'] < 0.5 - differenceThreshold:
                    problematicSplits.append({'split': key, 'problem': 3})
                elif percentiles[key]['Conversion'] < 0.5 - differenceThreshold and percentiles[key]['rAverage'] > 0.5 + differenceThreshold:
                    problematicSplits.append({'split': key, 'problem': 4})

        for split in problematicSplits:
            if split['problem'] == 1:
                text += 'You are resetting too soft ' + textDict[split['split']] + '\n'
            elif split['problem'] == 2:
                text += 'You are resetting too hard ' + textDict[split['split']] + '\n'
            elif split['problem'] == 3:
                text += 'You are playing exceptionally ' + textDict[split['split']] + '\n'
            elif split['problem'] == 4:
                text += 'Your gameplay needs a little bit of work ' + textDict[split['split']] + '\n'

        if text != '':
            text = 'When comparing your stats to the stats of other people who are near your skill level, we have determined that...\n' + text
        else:
            text = 'When comparing your stats to the stats of other people who are near your skill level, we have determined that...\n' + 'There is nothing unusual in your gameplay and resetting'
        return text

    @classmethod
    def overworld(cls, data):
        text = ''
        recomendedSeedsPlayed = None

        # wall seeds played
        for item in thresholds['recomendedSeedsPlayed']:
            if item['instMin'] <= int(settings['playstyle']['instance count']) <= item['instMax']:
                recomendedSeedsPlayed = {'a': item['lowerBound'], 'b': item['upperBound']}

        if recomendedSeedsPlayed is not None:
            if (data['general stats']['percent played'] < recomendedSeedsPlayed['a']):
                text += 'click into more seeds; be less picky with the previews you want to play\n'
            elif (data['general stats']['percent played'] > recomendedSeedsPlayed['b']):
                text += 'click into less seeds; be more selective with the previews you want to play\n'

        # overall reset hardness
        fast = data['general stats']['average enter'] > thresholds['splitFormulas']['Nether']['m'] * int(settings['playstyle']['target time']) + thresholds['splitFormulas']['Nether']['b']
        if data['general stats']['rnph'] < thresholds['nph']['low'] and fast:
            text += 'consider resetting your overworlds less aggressively; reset softer\n'
        if data['general stats']['rnph'] > thresholds['nph']['high'] and not fast:
            text += 'consider resetting your overworlds more agressively; reset harder\n'

        # conversions
        eSuccess = data['general stats']['Exit Success']
        bt2WoodConversion = (eSuccess['Buried Treasure w/ tnt']['Wood Conversion'] * eSuccess['Buried Treasure w/ tnt']['Iron Count'] + eSuccess['Buried Treasure']['Wood Conversion'] * eSuccess['Buried Treasure']['Iron Count']) / (eSuccess['Buried Treasure w/ tnt']['Iron Count'] + eSuccess['Buried Treasure']['Iron Count'])
        if bt2WoodConversion > thresholds['owConversions']['bt-wood']['high']:
            text += 'you might be playing out too many buried treasures; remember to judge ocean quality and pace while running to trees, and reset if they are not favourable\n'
        elif bt2WoodConversion < thresholds['owConversions']['bt-wood']['low']:
            text += 'if you play out islands that do not have trees, stop doing that; consider doing more thorough assessment of ocean quality while looking for the bt\n'

        played2btConversion = data['splits stats']['Iron']['Count']/data['general stats']['percent played']/data['general stats']['total resets']
        if played2btConversion < thresholds['owConversions']['played-bt']['low']:
            text += 'If you are resetting for mapless buried treasure, you might want to work on your mapless; you may be to selective with the spikes you play out for mapless'

        return text

    @classmethod
    def nether(cls, data):
        try:
            return Feedback.percentilesToText(Feedback.splitDataPercentiles(data), float(settings['display']['comparison threshold']))
        except Exception as e:
            return ''


class CompareProfiles:
    pass


# tracking
class Sheets:
    @classmethod
    def authenticate(cls):
        try:
            gc_sheets = pygsheets.authorize(service_file="credentials.json")
            sh = gc_sheets.open_by_url(settings['tracking']['sheet link'])
            wks = sh.worksheet_by_title('Raw Data')
        except Exception as e:
            print(e)
            return -1
        return wks

    @classmethod
    def setup(cls):
        wks1.update_row(index=1, values=['Date and Time', 'Iron Source', 'Enter Type', 'Gold Source', 'Spawn Biome', 'RTA', 'Wood', 'Iron Pickaxe', 'Nether', 'Bastion', 'Fortress', 'Nether Exit', 'Stronghold', 'End', 'Retimed IGT', 'IGT', 'Gold Dropped', 'Blaze Rods', 'Blazes', 'Flint', 'Gravel', 'Deaths', 'Traded', 'Endermen', 'Eyes Thrown', 'Iron', 'Wall Resets Since Prev', 'Played Since Prev', 'RTA Since Prev', 'Break RTA Since Prev', 'Wall Time Since Prev', 'Session Marker', 'RTA Distribution'], col_offset=0)

    @classmethod
    def sheets(cls):
        try:
            # Setting up constants and verifying
            color = (15.0, 15.0, 15.0)
            global pushedLines
            pushedLines = 1
            statsCsv = "temp.csv"
            def push_data():
                global pushedLines
                with open(statsCsv, newline="") as f:
                    reader = csv.reader(f)
                    data = list(reader)
                    f.close()
                try:
                    if len(data) == 0:
                        return
                    wks1.insert_rows(values=data, row=2, number=1, inherit=False)
                    wks1.insert_rows(values=data, row=1, number=1, inherit=False)
                    if pushedLines == 1:
                        endColumn = ord("A") + len(data)
                        endColumn1 = ord("A") + (endColumn // ord("A")) - 1
                        endColumn2 = ord("A") + ((endColumn - ord("A")) % 26)
                        endColumn = chr(endColumn1) + chr(endColumn2)
                        # dataSheet.format("A2:" + endColumn + str(1 + len(data)),{"backgroundColor": {"red": color[0], "green": color[1], "blue": color[2]}})
                    pushedLines += len(data)
                    f = open(statsCsv, "w+")
                    f.close()



                except Exception as e2:
                    print(e2)

            live = True
            while live:
                push_data()
                time.sleep(5)
        except Exception as e:
            print(e)
            input("")


# tracking
class NewRecord(FileSystemEventHandler):
    buffer = None
    sessionStart = None
    buffer_observer = None
    prev = None
    src_path = None
    prev_datetime = None
    wall_resets = 0
    rta_spent = 0
    splitless_count = 0
    break_time = 0
    wall_time = 0
    rtaString = ''
    isFirstRun = None

    def __init__(self):
        self.path = None
        self.data = None
        with main1.currentSessionMarkerLock:
            self.isFirstRun = currentSessionMarker + '$' + config['version']

    def ensure_run(self):
        if self.path is None:
            return False, "Path error"
        if self.data is None:
            return False, "Empty data error"
        if self.data['run_type'] != 'random_seed':
            return False, "Set seed detected, will not track"
        return True, ""

    def on_created(self, evt):
        self.this_run = [None] * (len(advChecks) + 2 + len(statsChecks))
        self.path = evt.src_path
        with open(self.path, "r") as record_file:
            try:
                self.data = json.load(record_file)
            except Exception as e:
                return
        if self.data is None:
            print("Record file couldnt be read")
            return
        validation = self.ensure_run()
        if not validation[0]:
            print(validation[1])
            return

        # Calculate breaks
        if self.prev_datetime is not None:
            run_differ = (datetime.now() - self.prev_datetime) - timedelta(milliseconds=self.data["final_rta"])
            if run_differ < timedelta(0):
                self.data['final_rta'] = self.data["final_igt"]
                run_differ = (datetime.now() - self.prev_datetime) - timedelta(milliseconds=self.data["final_rta"])
            if 'Projector' in Logistics.getForegroundWindowTitle() or settings['playstyle']["instance count"] == "1":
                if run_differ > timedelta(seconds=int(settings["tracking"]["break threshold"])):
                    self.break_time += run_differ.total_seconds() * 1000
                else:
                    self.wall_time += run_differ.total_seconds() * 1000
                self.prev_datetime = datetime.now()

        else:
            self.prev_datetime = datetime.now()

        if self.data["final_rta"] == 0:
            self.wall_resets += 1
            return
        uids = list(self.data["stats"].keys())
        if len(uids) == 0:
            print('no stats')
            return
        stats = self.data["stats"][uids[0]]["stats"]
        adv = self.data["advancements"]
        lan = self.data["open_lan"]
        if lan is not None:
            lan = int(lan)
        else:
            lan = math.inf

        # Advancements
        has_done_something = False
        self.this_run[0] = Logistics.ms_to_string(self.data["final_rta"])
        for idx in range(len(advChecks)):
            # Prefer to read from timelines
            if advChecks[idx][0] == "timelines" and self.this_run[idx + 1] is None:
                for tl in self.data["timelines"]:
                    if tl["name"] == advChecks[idx][1]:
                        if lan > int(tl["rta"]):
                            self.this_run[idx + 1] = Logistics.ms_to_string(tl["igt"])
                            has_done_something = True
            # Read other stuff from advancements
            elif (advChecks[idx][0] in adv and adv[advChecks[idx][0]]["complete"] and self.this_run[idx + 1] is None):
                if lan > int(adv[advChecks[idx][0]]["criteria"][advChecks[idx][1]]["rta"]):
                    self.this_run[idx +
                                  1] = Logistics.ms_to_string(adv[advChecks[idx][0]]["criteria"][advChecks[idx][1]]["igt"])
                    has_done_something = True
            # diamond pick
            elif (idx == 1) and ("minecraft:crafted" in stats and "minecraft:diamond_pickaxe" in stats["minecraft:crafted"]) and ("minecraft:recipes/misc/iron_nugget_from_smelting" in adv and adv["minecraft:recipes/misc/iron_nugget_from_smelting"]["complete"]) and self.this_run[idx + 1] is None:
                if lan > int(adv["minecraft:recipes/misc/iron_nugget_from_smelting"]["criteria"]["has_iron_axe"]["rta"]):
                    self.this_run[idx + 1] = Logistics.ms_to_string(adv["minecraft:recipes/misc/iron_nugget_from_smelting"]["criteria"]["has_iron_axe"]["igt"])
                    has_done_something = True

        if "minecraft:story/smelt_iron" in adv:
            has_done_something = True

        # If nothing was done, just count as reset
        if not has_done_something:
            # From earlier we know that final_rta > 0 so this is a splitless non-wall/bg reset
            self.splitless_count += 1
            # Only account for splitless RTA
            self.rta_spent += self.data["final_rta"]
            self.rtaString += str(math.trunc(self.data["final_rta"]/1000)) + '$'
            return

        self.rtaString += str(math.trunc(self.data["final_rta"]/1000))

        # Stats
        self.this_run[len(advChecks) + 1] = Logistics.ms_to_string(
            self.data["final_igt"])
        self.this_run[len(advChecks) + 2] = Logistics.ms_to_string(
            self.data["retimed_igt"])
        for idx in range(1, len(statsChecks)):
            if (
                statsChecks[idx][0] in stats
                and statsChecks[idx][1] in stats[statsChecks[idx][0]]
            ):
                self.this_run[len(advChecks) + 2 + idx] = str(
                    stats[statsChecks[idx][0]][statsChecks[idx][1]]
                )

        # Generate other stuff
        enter_type, gold_source, spawn_biome, iron_source = Tracking.getMiscData(stats, adv)

        iron_time = adv["minecraft:story/smelt_iron"]["igt"] if "minecraft:story/smelt_iron" in adv else None

        # Push to csv
        d = Logistics.ms_to_string(int(self.data["date"]), returnTime=True)
        data = ([str(d), iron_source, enter_type, gold_source, spawn_biome] + self.this_run +
                [Logistics.ms_to_string(iron_time), str(self.wall_resets), str(self.splitless_count),
                 Logistics.ms_to_string(self.rta_spent), Logistics.ms_to_string(self.break_time), Logistics.ms_to_string(self.wall_time), self.isFirstRun, self.rtaString])
        self.isFirstRun = ''

        with open("stats.csv", "a", newline="") as outfile:
            writer = csv.writer(outfile)
            writer.writerow(data)

        if settings['tracking']['use sheets'] == 1:
            with open("temp.csv", "r") as infile:
                reader = list(csv.reader(infile))
                reader.insert(0, data)
            with open("temp.csv", "w", newline="") as outfile:
                writer = csv.writer(outfile)
                for line in reader:
                    writer.writerow(line)

        # updates displayed stats
        CurrentSession.updateCurrentSession(data)


        # Reset all counters/sums
        self.wall_resets = 0
        self.rta_spent = 0
        self.splitless_count = 0
        self.wall_time = 0
        self.break_time = 0
        self.rtaString = ''


# tracking
class Tracking:
    @classmethod
    def getMiscData(cls, stats, adv):
        enter_type = "None"
        if "minecraft:story/enter_the_nether" in adv:
            enter_type = "Obsidian"
            if "minecraft:mined" in stats and "minecraft:magma_block" in stats["minecraft:mined"]:
                if "minecraft:story/lava_bucket" in adv:
                    enter_type = "Magma Ravine"
                else:
                    enter_type = "Bucketless"
            elif "minecraft:story/lava_bucket" in adv:
                enter_type = "Lava Pool"

        gold_source = "None"
        if ("minecraft:dropped" in stats and "minecraft:gold_ingot" in stats["minecraft:dropped"]) or (
                "minecraft:picked_up" in stats and (
                "minecraft:gold_ingot" in stats["minecraft:picked_up"] or "minecraft:gold_block" in stats[
                "minecraft:picked_up"])):
            gold_source = "Classic"
            if "minecraft:mined" in stats and "minecraft:dark_prismarine" in stats["minecraft:mined"]:
                gold_source = "Monument"
            elif "minecraft:nether/find_bastion" in adv:
                gold_source = "Bastion"

        spawn_biome = "None"
        if "minecraft:adventure/adventuring_time" in adv:
            for biome in adv["minecraft:adventure/adventuring_time"]["criteria"]:
                if adv["minecraft:adventure/adventuring_time"]["criteria"][biome]["igt"] == 0:
                    spawn_biome = biome.split(":")[1]

        iron_source = "None"
        # if iron acquired
        if "minecraft:story/smelt_iron" in adv or "minecraft:story/iron_tools" in adv or (
                "minecraft:crafted" in stats and "minecraft:diamond_pickaxe" in stats["minecraft:crafted"]):
            iron_source = "Misc"
            # if iron not obtained before nether enter
            if ("minecraft:story/enter_the_nether" in adv and "minecraft:story/smelt_iron" in adv) and (int(adv[
                    "minecraft:story/enter_the_nether"]["igt"]) < int(adv["minecraft:story/smelt_iron"]["igt"])):
                iron_source = "Nether"
            # if furnace crafted and iron ore mined
            elif ("minecraft:crafted" in stats and "minecraft:furnace" in stats["minecraft:crafted"]) and (
                    "minecraft:mined" in stats and "minecraft:iron_ore" in stats["minecraft:mined"]):
                iron_source = "Structureless"
            # if haybale mined or iron golem killed or iron pickaxe obtained from chest
            elif ("minecraft:mined" in stats and "minecraft:hay_block" in stats["minecraft:mined"]) or (
                    "minecraft:killed" in stats and "minecraft:iron_golem" in stats["minecraft:killed"]) or (
                    not ("minecraft:crafted" in stats and ("minecraft:iron_pickaxe" in stats[
                        "minecraft:crafted"] or "minecraft:diamond_pickaxe" in stats["minecraft:crafted"])) and (
                            "minecraft:story/iron_tools" in adv)):
                iron_source = "Village"
            # if more than 7 tnt mined
            elif ("minecraft:mined" in stats and "minecraft:tnt" in stats["minecraft:mined"] and stats[
                    "minecraft:mined"]["minecraft:tnt"] > 7):
                iron_source = "Desert Temple"
            # if stepped foot in ocean or beach under 3 minutes
            elif "minecraft:adventure/adventuring_time" in adv:
                for biome in adv["minecraft:adventure/adventuring_time"]["criteria"]:
                    if ("beach" in biome or "ocean" in biome) and int(
                            adv["minecraft:adventure/adventuring_time"]["criteria"][biome]["igt"]) < 180000:
                        # if potato, wheat, or carrot obtained
                        if "minecraft:recipes/food/baked_potato" in adv or (
                                "minecraft:recipes/food/bread" in adv) or (
                                "minecraft:recipes/transportation/carrot_on_a_stick" in adv):
                            iron_source = "Full Shipwreck"
                        # if sus stew or rotten flesh eaten
                        elif "minecraft:used" in stats and ("minecraft:suspicious_stew" in stats[
                                "minecraft:used"] or "minecraft:rotten_flesh" in stats["minecraft:used"]):
                            iron_source = "Full Shipwreck"
                        # if tnt exploded
                        elif "minecraft:used" in stats and "minecraft:tnt" in stats["minecraft:used"]:
                            iron_source = "Buried Treasure w/ tnt"
                            # if cooked salmon or cod eaten
                        elif "minecraft:used" in stats and ("minecraft:cooked_salmon" in stats[
                                "minecraft:used"] or "minecraft:cooked_cod" in stats["minecraft:used"]):
                            iron_source = "Buried Treasure"
                        # if sand/gravel mined before iron acquired
                        elif "minecraft:recipes/building_blocks/magenta_concrete_powder" in adv and (
                                adv["minecraft:recipes/building_blocks/magenta_concrete_powder"]["criteria"][
                                    "has_the_recipe"]["igt"] < adv["minecraft:story/smelt_iron"]["igt"]):
                            iron_source = "Buried Treasure"
                        # if wood mined before iron obtained
                        elif (("minecraft:story/smelt_iron" in adv and "minecraft:recipes/misc/charcoal" in adv) and (
                                int(adv["minecraft:story/smelt_iron"]["igt"]) > int(
                                adv["minecraft:recipes/misc/charcoal"][
                                "igt"]))) or ("minecraft:recipes/misc/charcoal" in adv and not (
                                "minecraft:story/iron_tools" in adv)):
                            if ("minecraft:custom" in stats and ("minecraft:open_chest" in stats[
                                "minecraft:custom"] and stats["minecraft:custom"][
                                                                     "minecraft:open_chest"] == 1)) or (
                                    "minecraft:nether/find_bastion" in adv):
                                iron_source = "Half Shipwreck"
                            else:
                                iron_source = "Full Shipwreck"
                        elif ("minecraft:crafted" in stats and "minecraft:diamond_pickaxe" in stats[
                            "minecraft:crafted"]) or (
                                "minecraft:crafted" in stats and "minecraft:diamond_sword" in stats[
                                "minecraft:crafted"]):
                            iron_source = "Buried Treasure"
                        elif "minecraft:mined" in stats and (("minecraft:oak_log" in stats["minecraft:mined"] and stats[
                                "minecraft:mined"]["minecraft:oak_log"] <= 4) or ("minecraft:dark_oak_log" in stats[
                                "minecraft:mined"] and stats["minecraft:mined"]["minecraft:dark_oak_log"] <= 4) or (
                                "minecraft:birch_log" in stats["minecraft:mined"] and stats["minecraft:mined"][
                                "minecraft:birch_log"] <= 4) or ("minecraft:jungle_log" in stats[
                                "minecraft:mined"] and stats["minecraft:mined"]["minecraft:jungle_log"] <= 4) or (
                                "minecraft:spruce_log" in stats["minecraft:mined"] and stats["minecraft:mined"][
                                "minecraft:spruce_log"] <= 4) or ("minecraft:acacia_log" in stats[
                                "minecraft:mined"] and stats["minecraft:mined"]["minecraft:acacia_log"] <= 4)):
                            iron_source = "Half Shipwreck"
                        else:
                            iron_source = "Buried Treasure"
        return enter_type, gold_source, spawn_biome, iron_source

    @classmethod
    def trackOldRecords(cls):
        pass

    @classmethod
    def trackResets(cls):
        if settings['tracking']['use sheets'] == 1:
            Sheets.setup()
            try:
                open("temp.csv", "x")
            except Exception as e:
                pass
        while True:
            try:
                newRecordObserver = Observer()
                event_handler = NewRecord()
                newRecordObserver.schedule(
                    event_handler, settings['tracking']["records path"], recursive=False)
                newRecordObserver.start()
            except Exception as e:
                print("Records directory could not be found")
            else:
                break
        if settings['tracking']["delete-old-records"] == 1:
            files = glob.glob(f'{settings["tracking"]["records path"]}\\*.json')
            for f in files:
                os.remove(f)

        if settings['tracking']['use sheets'] == 1:
            t = threading.Thread(target=Sheets.sheets, name="sheets")
            t.daemon = True
            t.start()

        print("Tracking...")
        live = True

        try:
            while live:
                if not isTracking:
                    live = False
                time.sleep(1)
        except Exception as e:
            print(e)
        finally:
            newRecordObserver.stop()
            newRecordObserver.join()


# gui
class IntroPage(Page):
    def populate(self):
        pass

    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        IntroPage.populate(self)


# gui
class SettingsPage(Page):
    explanationText = 'This is the page where you adjust your settings. Your settings are saved in the data folder. Remember to press save to save and apply the adjustments!'
    varStrings = [['sheet link', 'records path', 'break threshold', 'use sheets', 'delete-old-records', 'autoupdate stats'],
                  ['vault directory', 'twitch username', 'latest x sessions', 'comparison threshold', 'use local timezone', 'upload anonymity', 'use KDE'],
                  ['instance count', 'target time', 'rd', 'ed'],
                  ['Buried Treasure w/ tnt', 'Buried Treasure', 'Full Shipwreck', 'Half Shipwreck', 'Village']]
    varTypes = [['entry', 'entry', 'entry', 'check', 'check', 'check'],
                ['entry', 'entry', 'entry', 'entry', 'check', 'check', 'check'],
                ['entry', 'entry', 'entry', 'entry'],
                ['check', 'check', 'check', 'check', 'check']]
    varTooltips = [['', 'path to your records file, by default C:/Users/<user>/speedrunigt', 'after not having any resets while on wall for this many seconds, the tracker pauses until you reset again', 'if checked, data will be stored both locally and virtually via google sheets', '', 'if checked, the program will update and analyze your stats every time you stop tracking'],
                   ['currently not used', 'currently not used', 'when selecting a session, you can also select latest x sessions, which would depend on the integer for this setting', 'when generating feedback, the program compares you to players with in this number of seconds of your target time', 'if checked, the program will calculate session starts/ends in your timezone instead of utc', 'if checked, your twitch username will not be shown on the global sheet', 'if checked, histograms will display as kdeplots'],
                   ['', 'in seconds', '', 'numerical value from 0.5 to 5.0'],
                   ['', '', '', '', '']]
    varGroups = ['tracking', 'display', 'playstyle', 'playstyle cont.']
    settingsVars = []
    labels = []
    widgets = []
    containers = []
    subcontainers = []

    def saveSettings(self):
        global settings
        global wks1

        for i1 in range(len(self.varStrings)):
            for i2 in range(len(self.varStrings[i1])):
                if self.varStrings[i1][i2] in ["instance count", "target time", "latest x sessions", "comparison threshold", "break threshold", "rd", "ed"]:
                    if self.varStrings[i1][i2] == "ed":
                        try:
                            temp = float(self.settingsVars[i1][i2].get())
                            if not 0.5 <= temp <= 5.0:
                                raise Exception("NotInRange")
                        except Exception as e:
                            main1.errorPoppup(f'{self.varStrings[i1][i2]} must be a valid float between 0.5 and 5.0')
                            return
                    elif self.varStrings[i1][i2] == "rd":
                        try:
                            temp = int(self.settingsVars[i1][i2].get())
                            if not 2 <= temp <= 32:
                                raise Exception("NotInRange")
                        except Exception as e:
                            main1.errorPoppup(f'{self.varStrings[i1][i2]} must be a valid int between 2 and 32')
                            return
                    elif self.varStrings[i1][i2] == "target time":
                        try:
                            temp = int(self.settingsVars[i1][i2].get())
                            if not 240 <= temp:
                                raise Exception("NotInRange")
                        except Exception as e:
                            main1.errorPoppup(f'{self.varStrings[i1][i2]} must be a valid integer. it should be your target time IN SECONDS')
                            return
                    else:
                        try:
                            temp = int(self.settingsVars[i1][i2].get())
                        except Exception as e:
                            main1.errorPoppup(f'{self.varStrings[i1][i2]} must be a valid integer')
                            return
        for i1 in range(len(self.varStrings)):
            for i2 in range(len(self.varStrings[i1])):
                settings[self.varGroups[i1]][self.varStrings[i1][i2]] = self.settingsVars[i1][i2].get()

        try:
            settingsJson = open("data/settings.json", "w")
            json.dump(settings, settingsJson)
            settingsJson.close()
        except Exception as e:
            main1.errorPoppup('did you move your settings file from where it originally was?')

    def populate(self):
        explanation = Label(self, text=self.explanationText, wraplength=800, foreground='#1f0060', font=("Arial", 14))
        explanation.grid(row=0, column=0, columnspan=3, padx=50)
        loadedSettings = FileLoader.getSettings()
        for i1 in range(len(self.varStrings)):
            self.containers.append(tk.Frame(self, borderwidth=10))
            self.settingsVars.append([])
            self.labels.append([])
            self.widgets.append([])
            self.subcontainers.append([])
            for i2 in range(len(self.varStrings[i1])):
                self.subcontainers[i1].append(tk.Frame(self.containers[i1]))
                if self.varTypes[i1][i2] == 'entry':
                    self.settingsVars[i1].append(tk.StringVar())
                elif self.varTypes[i1][i2] == 'check':
                    self.settingsVars[i1].append(tk.IntVar())
                self.settingsVars[i1][i2].set(loadedSettings[self.varGroups[i1]][self.varStrings[i1][i2]])
                self.labels[i1].append(tk.Label(self.subcontainers[i1][i2], text=self.varStrings[i1][i2]))
                self.labels[i1][i2].pack(side="left")
                if self.varTypes[i1][i2] == 'entry':
                    self.widgets[i1].append(tk.Entry(self.subcontainers[i1][i2], textvariable=self.settingsVars[i1][i2]))
                elif self.varTypes[i1][i2] == 'check':
                    self.widgets[i1].append(tk.Checkbutton(self.subcontainers[i1][i2], text='', variable=self.settingsVars[i1][i2], onvalue=1, offvalue=0))
                self.widgets[i1][i2].pack(side="left")
                Tooltip.createToolTip(self.labels[i1][i2], self.varTooltips[i1][i2])
                self.subcontainers[i1][i2].pack(side="top")
        self.containers[0].grid(row=1, column=0, sticky="nsew")
        self.containers[1].grid(row=2, column=0, sticky="nsew")
        self.containers[2].grid(row=1, column=2, sticky="nsew")
        self.containers[3].grid(row=2, column=2, sticky="nsew")

        cmd = partial(self.saveSettings)
        save_Btn = tk.Button(self, text='Save', command=cmd)
        save_Btn.grid(row=3, column=1, sticky="nsew")


    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        SettingsPage.populate(self)


# gui
class CurrentSessionPage(Page):
    explanationText = 'Tables will appear here while you are tracking. They will provide data for the current session'
    frame = None

    def updateTables(self):
        self.frame.clear_widgets()
        self.frame.add_plot_frame(currentSession['figs'][0], 0, 0)
        self.frame.add_plot_frame(currentSession['figs'][1], 1, 0)

    def populate(self):
        explanation = Label(self, text=self.explanationText, wraplength=800, foreground='#1f0060', font=("Arial", 14))
        explanation.grid(row=0, column=0, padx=50)
        self.frame = ScrollableContainer(self)
        self.frame.grid(row=1, column=0)

    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        self.populate()


# gui
class GeneralPage(Page):
    explanationText = 'General stats, graphs, and tables will appear on this page. The most important statistics will appear on this page'
    frame = None

    def displayInfo(self):
        global isGraphingGeneral
        if not isGraphingGeneral:
            isGraphingGeneral = True
            sessionData = Stats.getSessionData(selectedSession.get(), sessions)

            self.frame.clear_widgets()
            self.frame.add_plot_frame(Graphs.graph11(sessionData['general stats']), 1, 0)
            self.frame.add_plot_frame(Graphs.graph12(sessionData['general stats']), 1, 1)
            self.frame.add_plot_frame(Graphs.graph8({'Wall': sessionData['general stats']['total Walltime'], 'Overworld': sessionData['general stats']['total ow time'], 'Nether': sessionData['general stats']['total nether time']}), 0, 2)
            self.frame.add_plot_frame(Graphs.graph1(sessionData['general stats']['RTA Distribution'], 'RTA', kde=(settings['display']['use KDE'] == 1)), 0, 0)
            self.frame.add_plot_frame(Graphs.graph13(sessionData['general stats']['IGT Distribution'], sessionData['general stats']['latest split list']), 0, 1)


    def populate(self):
        explanation = Label(self, text=self.explanationText, wraplength=800, foreground='#1f0060', font=("Arial", 14))
        explanation.grid(row=0, column=0, columnspan=2, padx=50)

        self.frame = ScrollableContainer(self)
        self.frame.grid(row=1, column=1)

        cmd = partial(self.displayInfo)
        graph_Btn = tk.Button(self, text='Graph', command=cmd)
        graph_Btn.grid(row=1, column=0)

    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        GeneralPage.populate(self)


# gui
class SplitsPage(Page):
    explanationText = 'Select any split from the dropdown to set it to the active split. the graphs and tables will provide data and analysis on the active split.'
    frame = None
    selectedSplit = None
    selectedAdjustment = None
    splits = ['Iron', 'Wood', 'Iron Pickaxe', 'Nether', 'Structure 1', 'Structure 2', 'Nether Exit', 'Stronghold', 'End']

    def displayInfo(self):
        global isGraphingSplit
        if not isGraphingSplit:
            isGraphingSplit = True
            sessionData = Stats.getSessionData(selectedSession.get(), sessions)

            text = f"If you reset your slowest {self.selectedAdjustment.get() * 100}% of {self.selectedSplit.get()}s, your {self.selectedSplit.get()}s per hour would decrease by no more than {self.selectedAdjustment.get() * 100}%, while your avg would decrease from {np.mean(sessionData['splits stats'][self.selectedSplit.get()]['Cumulative Distribution']):.1f} to {np.mean(Logistics.remove_top_X_percent(sessionData['splits stats'][self.selectedSplit.get()]['Cumulative Distribution'], self.selectedAdjustment.get())):.1f}"

            self.frame.clear_widgets()
            self.frame.add_plot_frame(Graphs.graph1(sessionData['splits stats'][self.selectedSplit.get()]['Cumulative Distribution'], self.selectedSplit.get(), kde=(settings['display']['use KDE'] == 1), removeX=self.selectedAdjustment.get(), smoothness=0.5), 0, 0)
            self.frame.add_plot_frame(Graphs.graph5(sessionData['splits stats'][self.selectedSplit.get()]), 1, 1)
            self.frame.add_plot_frame(Graphs.graph15(sessionData, self.selectedSplit.get(), kde=(settings['display']['use KDE'] == 1)), 0, 1)
            self.frame.add_label(text, 1, 0)


            isGraphingSplit = False

    def populate(self):
        explanation = Label(self, text=self.explanationText, wraplength=800, foreground='#1f0060', font=("Arial", 14))
        explanation.grid(row=0, column=0, columnspan=3, padx=50)

        self.frame = ScrollableContainer(self)
        self.frame.grid(row=1, column=1, rowspan=4)

        self.selectedSplit = StringVar()
        self.selectedSplit.set("Nether")
        drop1 = OptionMenu(self, self.selectedSplit, *self.splits)
        drop1.grid(row=1, column=0)

        self.selectedAdjustment = DoubleVar()
        self.selectedAdjustment.set(0.1)
        scale1 = Scale(self, variable=self.selectedAdjustment, from_=0.0, to=0.5, orient=tk.HORIZONTAL, resolution=0.01)
        scale1.grid(row=2, column=0)

        cmd = partial(self.displayInfo)
        graph_Btn = tk.Button(self, text='Graph', command=cmd)
        graph_Btn.grid(row=3, column=0)

    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        SplitsPage.populate(self)


# gui
class EntryBreakdownPage(Page):
    explanationText = 'This page focusses on the overworld. It does analysis based on the different iron sources and enter types that were used to enter the nether.'
    frame = None

    def displayInfo(self):
        global isGraphingEntry
        if not isGraphingEntry:
            isGraphingEntry = True
            sessionData = Stats.getSessionData(selectedSession.get(), sessions)
            enterTypeList = []
            enterMethodList = []
            for enter in sessionData['general stats']['enters']:
                enterTypeList.append(enter['type'])
                enterMethodList.append(enter['method'])

            self.frame.clear_widgets()
            self.frame.add_plot_frame(Graphs.graph4(sessionData['general stats']['enters'], settings), 0, 0)
            self.frame.add_plot_frame(Graphs.graph2(enterTypeList), 0, 1)
            self.frame.add_plot_frame(Graphs.graph2(enterMethodList), 1, 0)
            self.frame.add_plot_frame(Graphs.graph10(sessionData['general stats']['Exit Success']), 1, 1)

            isGraphingEntry = False


    def populate(self):
        explanation = Label(self, text=self.explanationText, wraplength=800, foreground='#1f0060', font=("Arial", 14))
        explanation.grid(row=0, column=0, columnspan=2, padx=50)

        self.frame = ScrollableContainer(self)
        self.frame.grid(row=1, column=1)

        cmd = partial(self.displayInfo)
        graph_Btn = tk.Button(self, text='Graph', command=cmd)
        graph_Btn.grid(row=1, column=0)

    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        EntryBreakdownPage.populate(self)


# gui
class ComparisonPage(Page):
    frame = None

    def displayInfo(self):
        global isGraphingComparison
        if not isGraphingComparison:
            isGraphingComparison = True

            self.frame.add_plot_frame(Graphs.graph9(sessions), 0, 0)

            isGraphingComparison = False

    def populate(self):
        self.frame = ScrollableContainer(self)
        self.frame.grid(row=0, column=1)

        cmd = partial(self.displayInfo)
        graph_Btn = tk.Button(self, text='Graph', command=cmd)
        graph_Btn.grid(row=0, column=0)

    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        ComparisonPage.populate(self)


# gui
class FeedbackPage(Page):
    explanationText = 'Generates Textual Feedback'
    panel1 = None
    panel2 = None
    container = None

    def displayInfo(self):
        global isGivingFeedback
        if not isGivingFeedback:
            isGivingFeedback = True
            sessionData = Stats.getSessionData(selectedSession.get(), sessions)

            try:
                self.panel1.set_text("Feedback:\n" + Feedback.overworld(sessionData))
            except Exception as e:
                self.panel1.set_text('An error occured')
                print(e)

            try:
                self.panel2.set_text("Feedback:\n" + Feedback.nether(sessionData))
            except Exception as e:
                self.panel2.set_text('An error occured')
                print(e)

            isGivingFeedback = False


    def populate(self):
        explanation = Label(self, text=self.explanationText, wraplength=800, foreground='#1f0060', font=("Arial", 14))
        explanation.grid(row=0, column=0, columnspan=2, padx=50)

        self.container = tk.Frame(self)
        self.container.grid(row=1, column=1)

        self.panel1 = ScrollableTextFrame(self.container)
        self.panel1.set_header('Overworld')
        self.panel1.grid(row=0, column=0, sticky="nsew")

        self.panel2 = ScrollableTextFrame(self.container)
        self.panel2.set_header('Nether')
        self.panel2.grid(row=1, column=0, sticky="nsew")

        cmd = partial(self.displayInfo)
        graph_Btn = tk.Button(self, text='Generate Feedback', command=cmd)
        graph_Btn.grid(row=1, column=0)

    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        self.populate()


# gui
class MainView(tk.Frame):
    top2 = None
    sessionMarkerInput = None
    txtFileNameInput = None
    selectedStat = None
    sessionMarkerEntry = None
    currentSessionMarkerLock = threading.Lock()
    pages = None
    trackingLabel = None
    updatingStatsLabel = None

    def authenticateSheets(self):
        if settings['tracking']['use sheets'] == 1:
            wks = Sheets.authenticate()
            if isinstance(wks, int):
                self.errorPoppup('sheet link might not be correct, also make sure credentials.json is in the same folder as exe')
            return wks
        else:
            return None

    def updateCSGraphs(self):
        self.pages[2].updateTables()

    def errorPoppup(self, text):
        top = Toplevel()
        top.geometry("300x200")
        top.title("Error")
        label = Label(top, text=text, wraplength=280)
        label.pack()

    def stopResetTracker(self):
        global isTracking
        isTracking = False
        self.trackingLabel.config(text='Tracking: False', foreground='red', background='black')

    def startResetTracker(self):
        global isTracking
        global wks1
        wks1 = self.authenticateSheets()
        if not isinstance(wks1, int):
            isTracking = True
            CurrentSession.resetCurrentSession()
            self.trackingLabel.config(text='Tracking: True', foreground='green', background='black')
            t1 = threading.Thread(target=Tracking.trackResets, name="tracker")
            t1.daemon = True
            t1.start()

    def promptUserForTracking(self):
        global currentSessionMarker
        if not isTracking:
            top1 = Toplevel()
            top1.geometry("180x100")
            top1.title("Start Tracking")

            label = Label(top1, text="Enter a Session Marker")
            label.pack()

            entry = Entry(top1)
            entry.pack()

            def get_value():
                global currentSessionMarker
                with self.currentSessionMarkerLock:
                    value = entry.get()
                    currentSessionMarker = value.replace('$', '')
                top1.destroy()
                self.startResetTracker()
                return value

            startTrackingButton = Button(top1, text="Start Tracking", command=get_value)
            startTrackingButton.pack()
        else:
            self.errorPoppup('Already Tracking')

    def updateData(self):
        global isUpdating
        self.updatingStatsLabel.config(text='Updating Stats: True', foreground='green', background='black')
        isUpdating = True
        Stats.saveSessionData(settings)
        self.updatingStatsLabel.config(text='Updating Stats: False', foreground='red', background='black')
        isUpdating = False

    def __init__(self, *args, **kwargs):
        global selectedSession
        tk.Frame.__init__(self, *args, **kwargs)
        pageTitles = ['About', 'Settings', 'Current Session', 'General', 'Splits', 'Entry Breakdown', 'Comparison', 'Feedback']
        self.pages = [IntroPage(self), SettingsPage(self), CurrentSessionPage(self), GeneralPage(self), SplitsPage(self), EntryBreakdownPage(self), ComparisonPage(self), FeedbackPage(self)]

        buttonframeMain = tk.Frame(self)
        buttonframe1 = tk.Frame(buttonframeMain)
        buttonframe2 = tk.Frame(buttonframeMain)
        container = tk.Frame(self)

        statsMenu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label='Stats', menu=statsMenu)
        statsMenu.add_command(label="Update Stats", command=self.updateData)
        statsMenu.add_command(label="Upload Data", command=Database.uploadData)

        trackingMenu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label='Tracking', menu=trackingMenu)
        trackingMenu.add_command(label="Start Tracking", command=self.promptUserForTracking)
        trackingMenu.add_command(label="Stop Tracking", command=self.stopResetTracker)
        trackingMenu.add_command(label="track old records", command=Tracking.trackOldRecords)

        updateMenu = Menu(menubar, tearoff=0)
        if Update.checkGithub():
            menubar.add_cascade(label='Update', menu=updateMenu)
            updateMenu.add_command(label="Update", command=Update.update)
        else:
            menubar.add_cascade(label='Update', menu=updateMenu)
        updateMenu.add_command(label="Open Github", command=Update.openGithub)

        resourcesMenu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label='Resources', menu=resourcesMenu)

        for i in range(len(self.pages)):
            self.pages[i].place(in_=container, x=0, y=0, relwidth=1, relheight=1)
            button = tk.Button(buttonframe1, text=pageTitles[i], command=self.pages[i].show, foreground='#ddddff', background='#880b00')
            button.grid(row=0, column=i, sticky="nsew")

        selectedSession = tk.StringVar()
        sessionStrings = []
        for session in sessions['sessions']:
            sessionStrings.append(session['string'])
        selectedSession.set(sessionStrings[0])
        drop = OptionMenu(buttonframeMain, selectedSession, *sessionStrings)
        drop.configure(background='black', foreground='white')
        self.trackingLabel = Label(buttonframeMain, text='Tracking: False', foreground="red", background='black', font=("Arial", 10), pady=3, padx=10)
        self.updatingStatsLabel = Label(buttonframeMain, text='Updating Stats: False', foreground="red", background='black', font=("Arial", 10), pady=3, padx=10)

        self.trackingLabel.pack(side="right", expand=True)
        self.updatingStatsLabel.pack(side="right", expand=True)
        drop.pack(side="right")
        buttonframe1.pack(side="left", fill="x", expand=False)
        buttonframeMain.pack(side="top")
        container.pack(side="top", fill="both", expand=True)

        self.pages[0].show()


if __name__ == "__main__":
    root = tk.Tk()
    root.title('Reset Tracker')
    menubar = Menu(root)
    main1 = MainView(root)
    root.config(menu=menubar)
    main1.pack(side="top", fill="both", expand=True)
    root.wm_geometry("1000x700")

    root.mainloop()
