import os
import shutil

"""
    STARTUP:
    Recreate data folder if not exists, copying it from the default folder
"""
if not os.path.exists("data"):
    os.makedirs("data")

for file in os.listdir("default"):
    if not os.path.exists(os.path.join("data", file)):
        shutil.copyfile(os.path.join("default", file), os.path.join("data", file))

from guiUtils import *


"""
global variables
"""
if True:

    if os.path.exists('stats.csv'):
        shutil.move('stats.csv', 'data/stats.csv')
    if os.path.exists('temp.csv'):
        shutil.move('temp.csv', 'data/temp.csv')

    if os.path.exists('data/stats.csv'):
        Stats.fixCSV()

    databaseLink = "https://docs.google.com/spreadsheets/d/1ky0mgYjsDE14xccw6JjmsKPrEIDHpt4TFnD2vr4Qmcc"
    lastRun = None
    config = FileLoader.getConfig()
    settings = FileLoader.getSettings()
    try:
        with open('data/stats.csv', 'x') as f:
            pass
    except Exception as e:
        pass
    if settings['tracking']['autoupdate stats'] == 1:
        lastRun = Stats.appendStats(settings, lastRun)
    sessions = FileLoader.getSessions()
    thresholds = FileLoader.getThresholds()
    wks1 = -1
    if getattr(sys, 'frozen', False):  # if running in a PyInstaller bundle
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    if(settings['tracking']['addToGlobalDatabase'] == 1):
        databasePath = os.path.join(base_path, 'databaseCredentials.json')
        if not os.path.exists(databasePath):
            print("DM pncakespoon#4895 on Discord to obtain the credentials file, then put it in the tracker folder. Or Disable tracking.addToGlobalDatabase in settings.json")
            sys.exit()
        gc_sheets_database = pygsheets.authorize(service_file=databasePath)
        sh2 = gc_sheets_database.open_by_url(databaseLink)
        wks2 = sh2[0]
    second = timedelta(seconds=1)
    currentSession = {'splits stats': {}, 'general stats': {}}
    currentSessionMarker = 'X'

    selectedSession = None
    isTracking = False
    isGraphingGeneral = False
    isGraphingSplit = False
    isGraphingEntry = False
    isGraphingComparison = False
    isGivingFeedback = False
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
        ("minecraft:crafted", "minecraft:diamond_pickaxe"),
        ("minecraft:used", "minecraft:ender_pearl"),
        ("minecraft:custom", "minecraft:deaths"),
        ("minecraft:used", "minecraft:obsidian"),
        ("minecraft:crafted", "minecraft:diamond_sword")
    ]

    blocks = ['minecraft:gravel',
             'minecraft:dirt',
             'minecraft:sand',
             'minecraft:soul_sand',
             'minecraft:soul_soil',
             'minecraft:stone',
             'minecraft:andesite',
             'minecraft:diorite',
             'minecraft:granite',
             'minecraft:gold_block',
             'minecraft:basalt',
             'minecraft:netherack',
             'minecraft:nether_bricks',
             'minecraft:blackstone',
             'minecraft:blackstone_wall',
             'minecraft:blackstone_slab',
             'minecraft:blackstone_stairs',
             'minecraft:gilded_blackstone',
             'minecraft:blackstone',
             'minecraft:polished_blackstone_bricks',
             'minecraft:chiseled_polished_blackstone',
             'minecraft:polished_blackstone_brick_wall',
             'minecraft:polished_blackstone_brick_slab',
             'minecraft:polished_blackstone_brick_stairs',
             'minecraft:cracked_polished_blackstone_bricks',
             'minecraft:crafting_table',
             'minecraft:oak_log',
             'minecraft:birch_log',
             'minecraft:spruce_log',
             'minecraft:jungle_log',
             'minecraft:acacia_log',
             'minecraft:dark_oak_log',
             'minecraft:warped_stem',
             'minecraft:crimson_stem',
             'minecraft:oak_leaves',
             'minecraft:birch_leaves',
             'minecraft:spruce_leaves',
             'minecraft:jungle_leaves',
             'minecraft:acacia_leaves',
             'minecraft:dark_oak_leaves'
             ]
"""
global variables
"""


class Update:
    @classmethod
    def checkGithub(cls):
        response = requests.get("https://api.github.com/repos/pncakespoon1/ResetTracker/releases/latest")
        # Check if the request was successful
        if response.status_code == 200:
            # Get the JSON data from the response
            release_data = response.json()

            # Extract the tag name from the release data
            latest_tag = release_data["tag_name"]
        else:
            return False
        if latest_tag == config['version']:
            return False
        else:
            return True

    @classmethod
    def update(cls):
        if not getattr(sys, 'frozen', False):
            subprocess.Popen('update.exe')
        else:
            subprocess.Popen('py update.py')
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
            configFile = open('data/config.json', 'w')
            json.dump(config, configFile)
            configFile.close()
        values = [config['lbName'], str(int(settings['playstyle']['instance count'])), str(int(settings['playstyle']['target time']))]
        for statistic in ['rnph', 'rpe', '% played', 'efficiency score']:
            values.append(careerData['general stats'][statistic])
        for statistic in ['Cumulative Average', 'Relative Average', 'Relative Conversion', 'xph']:
            for split in ['Iron', 'Wood', 'Iron Pickaxe', 'Nether', 'Structure 1', 'Structure 2', 'Nether Exit', 'Stronghold', 'End']:
                values.append(careerData['splits stats'][split][statistic])
        if settings['tracking']['addToGlobalDatabase'] == 1:
            if config['lbName'] in nameList:
                rownum = nameList.index(config['lbName']) + 1
                wks2.update_row(index=rownum - 1, values=values, col_offset=0)
            else:
                wks2.insert_rows(row=userCount, number=1, values=values, inherit=False)


class CurrentSession:
    @classmethod
    def updateCurrentSession(cls, row):
        global currentSession
        for i in range(len(row)):
            if row[i] == '':
                row[i] = None
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
        currentSession['general stats']['total RTA'] += rowCells['RTA'] + rowCells['RTA Since Prev'] + rowCells['Wall Time Since Prev']
        currentSession['general stats']['total wall resets'] += int(rowCells['Wall Resets Since Prev'])
        currentSession['general stats']['total played'] += int(rowCells['Played Since Prev']) + 1
        currentSession['general stats']['total wall time'] += rowCells['Wall Time Since Prev']

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
            print(16)
            print(e)
        try:
            currentSession['figs'][1] = Graphs.graph7(currentSession)
        except Exception as e:
            print(17)
            print(e)
            pass

        if __name__ == "__main__":
            main1.updateCSGraphs(row)
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


# class methods for giving feedback
class Feedback:
    @classmethod
    def splits(cls, split, average, formulaDict):
        targetTime = int(settings['playstyle']['target time'])
        return Logistics.getResidual(average, formulaDict[split]['m'], targetTime, formulaDict[split]['b'])

    @classmethod
    def splitsA(cls, split, average):
        formulaDict = thresholds['splitFormulas']
        return Feedback.splits(split, average, formulaDict)


    @classmethod
    def readDatabase(cls):
        similarUserList = []
        if(settings['tracking']['addToGlobalDatabase']) == 1 :
            targetTimeCol = wks2.get_col(col=3, returnas='matrix', include_tailing_empty=False)
            targetTimeCol.pop(0)
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
        reg_m, reg_b, reg_s, reg_r2, reg_p = Logistics.getRegressionLine(targetTimeList, scoreList)
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
        try:
            for item in thresholds['recomendedSeedsPlayed']:
                if item['instMin'] <= int(settings['playstyle']['instance count']) <= item['instMax']:
                    recomendedSeedsPlayed = {'a': item['lowerBound'], 'b': item['upperBound']}

            if recomendedSeedsPlayed is not None:
                if (data['general stats']['% played'] < recomendedSeedsPlayed['a']):
                    text += 'click into more seeds; be less picky with the previews you want to play\n'
                elif (data['general stats']['% played'] > recomendedSeedsPlayed['b']):
                    text += 'click into less seeds; be more selective with the previews you want to play\n'
        except Exception as e:
            print(18)
            print(e)

        # overall reset hardness
        try:
            fast = data['general stats']['average enter'] > thresholds['splitFormulas']['Nether']['m'] * int(settings['playstyle']['target time']) + thresholds['splitFormulas']['Nether']['b']
            if data['general stats']['rnph'] < thresholds['nph']['low'] and fast:
                text += 'consider resetting your overworlds less aggressively; reset softer\n'
            if data['general stats']['rnph'] > thresholds['nph']['high'] and not fast:
                text += 'consider resetting your overworlds more agressively; reset harder\n'
        except Exception as e:
            print(19)
            print(e)

        # conversions
        try:
            eSuccess = data['general stats']['Exit Success']
            bt2WoodConversion = (eSuccess['Buried Treasure w/ tnt']['Wood Conversion'] * eSuccess['Buried Treasure w/ tnt']['Iron Count'] + eSuccess['Buried Treasure']['Wood Conversion'] * eSuccess['Buried Treasure']['Iron Count']) / (eSuccess['Buried Treasure w/ tnt']['Iron Count'] + eSuccess['Buried Treasure']['Iron Count'])
            if bt2WoodConversion > thresholds['owConversions']['bt-wood']['high']:
                text += 'you might be playing out too many buried treasures; remember to judge ocean quality and pace while running to trees, and reset if they are not favourable\n'
            elif bt2WoodConversion < thresholds['owConversions']['bt-wood']['low']:
                text += 'if you play out islands that do not have trees, stop doing that; consider doing more thorough assessment of ocean quality while looking for the bt\n'
        except Exception as e:
            print(20)
            print(e)

        try:
            played2btConversion = data['splits stats']['Iron']['Count']/data['general stats']['% played']/data['general stats']['total resets']
            if played2btConversion < thresholds['owConversions']['played-bt']['low']:
                text += 'If you are resetting for mapless buried treasure, you might want to work on your mapless; you may be to selective with the spikes you play out for mapless'
        except Exception as e:
            print(21)
            print(e)

        return text

    @classmethod
    def nether(cls, data):
        text = ''

        try:
            for split in ['Structure 1', 'Structure 2', 'Nether Exit']:
                if data['splits stats'][split]['Cumulative Average'] - (thresholds['splitFormulas'][split]['m'] * int(settings['playstyle']['target time']) + thresholds['splitFormulas'][split]['b']) > 30:
                    text += f'your average {split} is a bit on the slow end\n'
        except Exception as e:
            print(22)
            print(e)

        return text


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
            return -1
        return wks

    @classmethod
    def setup(cls):
        wks1.update_row(index=1, values=headerLabels, col_offset=0)

    @classmethod
    def sheets(cls):
        try:
            # Setting up constants and verifying
            color = (15.0, 15.0, 15.0)
            global pushedLines
            pushedLines = 1

            def push_data():
                global pushedLines
                with open("data/temp.csv", newline="") as f:
                    reader = csv.reader(f)
                    data = list(reader)
                    f.close()
                try:
                    if len(data) == 0:
                        return
                    wks1.insert_rows(values=data, row=1, number=1, inherit=False)
                    if pushedLines == 1:
                        endColumn = ord("A") + len(data)
                        endColumn1 = ord("A") + (endColumn // ord("A")) - 1
                        endColumn2 = ord("A") + ((endColumn - ord("A")) % 26)
                        endColumn = chr(endColumn1) + chr(endColumn2)
                        # dataSheet.format("A2:" + endColumn + str(1 + len(data)),{"backgroundColor": {"red": color[0], "green": color[1], "blue": color[2]}})
                    pushedLines += len(data)
                    f = open("data/temp.csv", "w+")
                    f.close()



                except Exception as e2:
                    print(23)
                    print(e2)

            live = True
            while live:
                push_data()
                time.sleep(3)
        except Exception as e:
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
        if __name__ == "__main__":
            with main1.currentSessionMarkerLock:
                self.isFirstRun = currentSessionMarker + '$' + config['version']
        else:
            self.isFirstRun = currentSessionMarker + '$' + config['version']

    def ensure_run(self):
        if settings['tracking']['detect RSG'] == 0:
            return True, ""
        if self.path is None:
            return False, "Path error"
        if self.data is None:
            return False, "Empty data error"
        if self.data['run_type'] != 'random_seed':
            return False, "Set seed detected, will not track"
        return True, ""

    def on_created(self, evt, dt1=None):
        self.this_run = [''] * (len(advChecks) + 2 + len(statsChecks))
        self.path = evt.src_path
        with open(self.path, "r") as record_file:
            try:
                self.data = json.load(record_file)
            except Exception as e:
                print(24)
                print(e)
                time.sleep(1)
                self.on_created(evt)
                return
        if self.data is None:
            return
        validation = self.ensure_run()
        if not validation[0]:
            return
        if dt1 is None:
            now = datetime.now()
        else:
            now = datetime(year=1970, month=1, day=1, second=int(dt1/1000))
        # Calculate breaks
        if self.prev_datetime is not None:
            run_differ = (now - self.prev_datetime) - timedelta(milliseconds=self.data["final_rta"])
            if run_differ < timedelta(0):
                self.data['final_rta'] = self.data["final_igt"]
                run_differ = (now - self.prev_datetime) - timedelta(milliseconds=self.data["final_rta"])
            if Logistics.isOnWallScreen() or settings['playstyle']["instance count"] == "1":
                if run_differ > timedelta(seconds=int(settings["tracking"]["break threshold"])):
                    self.break_time += run_differ.total_seconds() * 1000
                else:
                    self.wall_time += run_differ.total_seconds() * 1000
                self.prev_datetime = now

        else:
            self.prev_datetime = now

        if self.data["final_rta"] == 0:
            self.wall_resets += 1
            return
        uids = list(self.data["stats"].keys())
        if len(uids) == 0:
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
            if advChecks[idx][0] == "timelines" and self.this_run[idx + 1] == '':
                for tl in self.data["timelines"]:
                    if tl["name"] == advChecks[idx][1]:
                        if lan > int(tl["rta"]):
                            self.this_run[idx + 1] = Logistics.ms_to_string(tl["igt"])
                            has_done_something = True
            # Read other stuff from advancements
            elif (advChecks[idx][0] in adv and adv[advChecks[idx][0]]["complete"] and self.this_run[idx + 1] == ''):
                if lan > int(adv[advChecks[idx][0]]["criteria"][advChecks[idx][1]]["rta"]):
                    self.this_run[idx +
                                  1] = Logistics.ms_to_string(adv[advChecks[idx][0]]["criteria"][advChecks[idx][1]]["igt"])
                    has_done_something = True
            # diamond pick
            elif (idx == 1) and ("minecraft:crafted" in stats and "minecraft:diamond_pickaxe" in stats["minecraft:crafted"]) and self.this_run[idx + 1] == '':
                if ("minecraft:recipes/misc/gold_nugget_from_smelting" in adv and adv["minecraft:recipes/misc/gold_nugget_from_smelting"]["complete"]) and ("has_gold_axe" in adv["minecraft:recipes/misc/gold_nugget_from_smelting"]["criteria"] and lan > int(adv["minecraft:recipes/misc/gold_nugget_from_smelting"]["criteria"]["has_gold_axe"]["rta"])):
                    self.this_run[idx + 1] = Logistics.ms_to_string(adv["minecraft:recipes/misc/gold_nugget_from_smelting"]["criteria"]["has_gold_axe"]["igt"])
                    has_done_something = True
                elif ("minecraft:recipes/misc/iron_nugget_from_smelting" in adv and adv["minecraft:recipes/misc/iron_nugget_from_smelting"]["complete"]) and ("has_iron_axe" in adv["minecraft:recipes/misc/iron_nugget_from_smelting"]["criteria"] and lan > int(adv["minecraft:recipes/misc/iron_nugget_from_smelting"]["criteria"]["has_iron_axe"]["rta"])):
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
        enter_type, gold_source, spawn_biome, iron_source, blocks_mined = Tracking.getMiscData(stats, adv)
        if settings['tracking']['track seed'] == 1:
            try:
                save_path = Logistics.find_save(settings['tracking']['MultiMC directory'], self.path, self.data["world_name"])
                nbtfile = nbt.load(save_path + "\\level.dat")
                seed = nbtfile["Data"]["WorldGenSettings"]["seed"]
                seed = re.sub(r'[^0-9]', '', str(seed))
            except Exception as e:
                print(e)
                seed = ""

        else:
            seed = ""

        iron_time = adv["minecraft:story/smelt_iron"]["igt"] if "minecraft:story/smelt_iron" in adv else None

        # Push to csv
        d = Logistics.ms_to_string(int(self.data["date"]), returnTime=True)
        data1 = ([str(d), iron_source, enter_type, gold_source, spawn_biome] + self.this_run[:-5] + [''] * 6 +
                [Logistics.ms_to_string(iron_time), str(self.wall_resets), str(self.splitless_count),
                 Logistics.ms_to_string(self.rta_spent), Logistics.ms_to_string(self.break_time), Logistics.ms_to_string(self.wall_time), self.isFirstRun, self.rtaString, seed] + self.this_run[-5:] + [blocks_mined])
        data2 = []
        for item in data1:
            if type(item) == str and ":" in item and item.count("-") < 2:
                data2.append("*" + item[:-3])
            else:
                data2.append(item)

        self.isFirstRun = ''

        with open("data/stats.csv", "a", newline="") as outfile:
            writer = csv.writer(outfile)
            writer.writerow(data1)

        if settings['tracking']['use sheets'] == 1:
            with open("data/temp.csv", "r") as infile:
                reader = list(csv.reader(infile))
                reader.insert(0, data2)
            with open("data/temp.csv", "w", newline="") as outfile:
                writer = csv.writer(outfile)
                for line in reader:
                    writer.writerow(line)

        # updates displayed stats
        if __name__ == "__main__":
            CurrentSession.updateCurrentSession(data1)


        # Reset all counters/sums
        self.wall_resets = 0
        self.rta_spent = 0
        self.splitless_count = 0
        self.wall_time = 0
        self.break_time = 0
        self.rtaString = ''



class OldRecord:
    sessionStart = None
    prev = None
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
        if __name__ == "__main__":
            with main1.currentSessionMarkerLock:
                self.isFirstRun = currentSessionMarker + '$' + config['version']
        else:
            self.isFirstRun = currentSessionMarker + '$' + config['version']


    def ensure_run(self):
        if settings['tracking']['detect RSG'] == 0:
            return True, ""
        if self.path is None:
            return False, "Path error"
        if self.data is None:
            return False, "Empty data error"
        if self.data['run_type'] != 'random_seed':
            return False, "Set seed detected, will not track"
        return True, ""

    def analyze_record(self, path):
        self.this_run = [''] * (len(advChecks) + 2 + len(statsChecks))
        self.path = path
        with open(self.path, "r") as record_file:
            try:
                self.data = json.load(record_file)
            except Exception as e:
                print(24)
                print(e)
                return
        if self.data is None:
            return
        validation = self.ensure_run()
        if not validation[0]:
            return
        now = datetime(year=1970, month=1, day=1, second=1) + timedelta(milliseconds=self.data['date'])
        # Calculate breaks
        if self.prev_datetime is not None:
            run_differ = (now - self.prev_datetime) - timedelta(milliseconds=self.data["final_rta"])
            if run_differ < timedelta(0):
                self.data['final_rta'] = self.data["final_igt"]
                run_differ = (now - self.prev_datetime) - timedelta(milliseconds=self.data["final_rta"])
            if Logistics.isOnWallScreen() or settings['playstyle']["instance count"] == "1":
                if run_differ > timedelta(seconds=int(settings["tracking"]["break threshold"])):
                    self.break_time += run_differ.total_seconds() * 1000
                else:
                    self.wall_time += run_differ.total_seconds() * 1000
                self.prev_datetime = now

        else:
            self.prev_datetime = now

        if self.data["final_rta"] == 0:
            self.wall_resets += 1
            return
        uids = list(self.data["stats"].keys())
        if len(uids) == 0:
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
            if advChecks[idx][0] == "timelines" and self.this_run[idx + 1] == '':
                for tl in self.data["timelines"]:
                    if tl["name"] == advChecks[idx][1]:
                        if lan > int(tl["rta"]):
                            self.this_run[idx + 1] = Logistics.ms_to_string(tl["igt"])
                            has_done_something = True
            # Read other stuff from advancements
            elif (advChecks[idx][0] in adv and adv[advChecks[idx][0]]["complete"] and self.this_run[idx + 1] == ''):
                if lan > int(adv[advChecks[idx][0]]["criteria"][advChecks[idx][1]]["rta"]):
                    self.this_run[idx +
                                  1] = Logistics.ms_to_string(adv[advChecks[idx][0]]["criteria"][advChecks[idx][1]]["igt"])
                    has_done_something = True
            # diamond pick
            elif (idx == 1) and ("minecraft:crafted" in stats and "minecraft:diamond_pickaxe" in stats["minecraft:crafted"]) and self.this_run[idx + 1] == '':
                if ("minecraft:recipes/misc/gold_nugget_from_smelting" in adv and adv["minecraft:recipes/misc/gold_nugget_from_smelting"]["complete"]) and ("has_gold_axe" in adv["minecraft:recipes/misc/gold_nugget_from_smelting"]["criteria"] and lan > int(adv["minecraft:recipes/misc/gold_nugget_from_smelting"]["criteria"]["has_gold_axe"]["rta"])):
                    self.this_run[idx + 1] = Logistics.ms_to_string(adv["minecraft:recipes/misc/gold_nugget_from_smelting"]["criteria"]["has_gold_axe"]["igt"])
                    has_done_something = True
                elif ("minecraft:recipes/misc/iron_nugget_from_smelting" in adv and adv["minecraft:recipes/misc/iron_nugget_from_smelting"]["complete"]) and ("has_iron_axe" in adv["minecraft:recipes/misc/iron_nugget_from_smelting"]["criteria"] and lan > int(adv["minecraft:recipes/misc/iron_nugget_from_smelting"]["criteria"]["has_iron_axe"]["rta"])):
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
        enter_type, gold_source, spawn_biome, iron_source, blocks_mined = Tracking.getMiscData(stats, adv)
        if settings['tracking']['track seed'] == 1:
            try:
                save_path = Logistics.find_save(settings['tracking']['MultiMC directory'], self.path, self.data["world_name"])
                nbtfile = nbt.load(save_path + "\\level.dat")
                seed = nbtfile["Data"]["WorldGenSettings"]["seed"]
                seed = re.sub(r'[^0-9]', '', str(seed))
            except Exception as e:
                print(e)
                seed = ""

        else:
            seed = ""

        iron_time = adv["minecraft:story/smelt_iron"]["igt"] if "minecraft:story/smelt_iron" in adv else None

        # Push to csv
        d = Logistics.ms_to_string(int(self.data["date"]), returnTime=True)
        data1 = ([str(d), iron_source, enter_type, gold_source, spawn_biome] + self.this_run[:-5] + [''] * 6 +
                [Logistics.ms_to_string(iron_time), str(self.wall_resets), str(self.splitless_count),
                 Logistics.ms_to_string(self.rta_spent), Logistics.ms_to_string(self.break_time), Logistics.ms_to_string(self.wall_time), self.isFirstRun, self.rtaString, seed] + self.this_run[-5:] + [blocks_mined])
        data2 = []
        for item in data1:
            if type(item) == str and ":" in item and item.count("-") < 2:
                data2.append("*" + item[:-3])
            else:
                data2.append(item)

        self.isFirstRun = ''

        with open("data/stats.csv", "a", newline="") as outfile:
            writer = csv.writer(outfile)
            writer.writerow(data1)

        if settings['tracking']['use sheets'] == 1:
            with open("data/temp.csv", "r") as infile:
                reader = list(csv.reader(infile))
                reader.insert(0, data2)
            with open("data/temp.csv", "w", newline="") as outfile:
                writer = csv.writer(outfile)
                for line in reader:
                    writer.writerow(line)

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

        blocks_mined_list = ['0'] * len(blocks)

        if "minecraft:mined" in stats:
            for i in range(len(blocks)):
                if blocks[i] in stats["minecraft:mined"]:
                    blocks_mined_list[i] = str(stats["minecraft:mined"][blocks[i]])

        blocks_mined = '$'.join(blocks_mined_list)

        return enter_type, gold_source, spawn_biome, iron_source, blocks_mined

    @classmethod
    def trackOldRecords(cls):
        directory = 'records'

        oldrecordtracker = OldRecord()

        # Get a list of all files in the directory with their creation timestamps
        files = [(filename, os.path.getctime(os.path.join(directory, filename)))
                 for filename in os.listdir(directory)
                 if os.path.isfile(os.path.join(directory, filename))]

        # Sort the files based on their creation timestamps in ascending order
        sorted_files = sorted(files, key=lambda x: x[1], reverse=True)

        # Print the file paths in order from oldest to newest
        for file in sorted_files:
            filepath = os.path.join(directory, file[0])
            oldrecordtracker.analyze_record(filepath)

        for file in sorted_files:
            filepath = os.path.join(directory, file[0])
            os.remove(filepath)


    @classmethod
    def trackResets(cls):
        if settings['tracking']['use sheets'] == 1:
            Sheets.setup()
            # Create temp.csv if it doesn't exist
            if not os.path.exists('data/temp.csv'):
                with open('data/temp.csv', 'w') as f:
                    f.write('')
  
        while True:
            try:
                newRecordObserver = Observer()
                event_handler = NewRecord()
                newRecordObserver.schedule(
                    event_handler, settings['tracking']["records path"], recursive=False)
                newRecordObserver.start()
            except Exception as e:
                if __name__ == "__main__":
                    main1.errorPoppup("Records directory could not be found")
                else:
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

        live = True

        try:
            while live:
                if __name__ == "__main__":
                    if not isTracking:
                        live = False
                time.sleep(3)
        except Exception as e:
            print(26)
            print(e)
        finally:
            newRecordObserver.stop()
            newRecordObserver.join()


# gui
class ControlPage(Page):
    def toggle_tracking(self):
        if isTracking:
            main1.stopResetTracker()
            self.set_button_color(True)
        else:
            main1.promptUserForTracking()

    def set_button_color(self, state):
        if not state:
            self.toggle_tracking_button.config(text='Stop Tracking', background=guiColors['false'])
        else:
            self.toggle_tracking_button.config(text='Start Tracking', background=guiColors['true'])

            
    def populate(self):
        # Create the buttons
        self.grid_columnconfigure(0, weight=1)

        self.toggle_tracking_button = Button(self, text="Start Tracking", command=self.toggle_tracking, background=guiColors['true'], foreground=guiColors['text'], font=('Arial', 48))
        self.toggle_tracking_button.grid(row=0, column=0, padx=10, pady=(60, 10))

        track_old_button = Button(self, text="Track Old Records", command=Tracking.trackOldRecords, background=guiColors['secondary'], foreground=guiColors['text'], font=('Arial', 24))
        track_old_button.grid(row=2, column=0, padx=10, pady=10)

        if Update.checkGithub():
            update_button = Button(self, text="Update", command=Update.update, background=guiColors['secondary'], foreground=guiColors['text'], font=('Arial', 24))
        else:
            update_button = Button(self, text="Update", state=tk.DISABLED, background=guiColors['secondary'], foreground=guiColors['text'], font=('Arial', 24))
        update_button.grid(row=3, column=0, padx=10, pady=10)

    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        self.populate()


# gui
class SettingsPage(Page):
    explanationText = 'This is the page where you adjust your settings. Your settings are saved in the data folder. Remember to press save to save and apply the adjustments!'
    varStrings = [['sheet link', 'records path', 'MultiMC directory', 'break threshold', 'use sheets', 'delete-old-records', 'autoupdate stats', 'detect RSG', 'track seed', 'track on launch'],
                  ['vault directory', 'twitch username', 'latest x sessions', 'comparison threshold', 'use local timezone', 'upload anonymity', 'use KDE'],
                  ['instance count', 'target time', 'rd', 'ed'],
                  ['Buried Treasure w/ tnt', 'Buried Treasure', 'Full Shipwreck', 'Half Shipwreck', 'Village']]
    varTypes = [['entry', 'entry', 'entry', 'entry', 'check', 'check', 'check', 'check', 'check', 'check'],
                ['entry', 'entry', 'entry', 'entry', 'check', 'check', 'check'],
                ['entry', 'entry', 'entry', 'entry'],
                ['check', 'check', 'check', 'check', 'check']]
    varTooltips = [['', 'path to your records file, by default C:/Users/<user>/speedrunigt/records', 'path to multimc', 'after not having any resets while on wall for this many seconds, the tracker pauses until you reset again', 'if checked, data will be stored both locally and virtually via google sheets', '', 'if checked, the program will update and analyze your stats every time it launches', 'Only track random seed runs. Disable for other categories.', '', ''],
                   ['currently not used', 'currently not used', 'when selecting a session, you can also select latest x sessions, which would depend on the integer for this setting', 'when generating feedback, the program compares you to players with in this number of seconds of your target time', 'if checked, the program will calculate session starts/ends in your timezone instead of utc', 'if checked, your twitch username will not be shown on the global sheet', 'if checked, histograms will display as kdeplots'],
                   ['', 'in seconds', '', 'numerical value from 0.5 to 5.0'],
                   ['', '', '', '', '']]
    varGroups = ['tracking', 'display', 'playstyle', 'playstyle cont.']
    settingsVars = []
    labels = []
    widgets = []
    containers = []

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
                    elif self.varStrings[i1][i2] == 'MultiMC directory':
                        if (self.settingsVars[i1][i2].get() == "" or not os.path.exists(self.settingsVars[i1][i2].get())) and self.settingsVars[self.varGroups.index('tracking')][self.varStrings[self.varGroups.index('track seed')]].get() == 1:
                            main1.errorPoppup('track seed is checked but MultiMC directory is not valid or does not exist.')

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
        explanation = Label(self, text=self.explanationText, wraplength=800, foreground=guiColors['text'], font=("Arial", 14))
        explanation.grid(row=0, column=0, columnspan=3, padx=50)
        loadedSettings = FileLoader.getSettings()
        for i1 in range(len(self.varStrings)):
            container = Frame(self, borderwidth=10)
            container.grid_columnconfigure(1, weight=1)
            self.containers.append(container)
            self.settingsVars.append([])
            self.labels.append([])
            self.widgets.append([])
            for i2 in range(len(self.varStrings[i1])):
                if self.varTypes[i1][i2] == 'entry':
                    self.settingsVars[i1].append(tk.StringVar())
                elif self.varTypes[i1][i2] == 'check':
                    self.settingsVars[i1].append(tk.IntVar())
                self.settingsVars[i1][i2].set(loadedSettings[self.varGroups[i1]][self.varStrings[i1][i2]])
                if self.varStrings[i1][i2] == 'vault directory':
                    self.labels[i1].append(Label(self.containers[i1], text=self.varStrings[i1][i2] + ' (irrelevant)'))
                else:
                    self.labels[i1].append(Label(self.containers[i1], text=self.varStrings[i1][i2]))
                self.labels[i1][i2].grid(row=i2, column=0, sticky='w')
                if self.varTypes[i1][i2] == 'entry':
                    widget = Entry(self.containers[i1], textvariable=self.settingsVars[i1][i2])
                    widget.config(bg=guiColors['white'])
                elif self.varTypes[i1][i2] == 'check':
                    widget = Checkbutton(self.containers[i1], text='', variable=self.settingsVars[i1][i2], onvalue=1, offvalue=0)
                self.widgets[i1].append(widget)
                self.widgets[i1][i2].grid(row=i2, column=2, sticky='e')
                Tooltip.createToolTip(self.labels[i1][i2], self.varTooltips[i1][i2])
        self.containers[0].grid(row=1, column=0, sticky="nsew")
        self.containers[1].grid(row=2, column=0, sticky="nsew")
        self.containers[2].grid(row=1, column=2, sticky="nsew")
        self.containers[3].grid(row=2, column=2, sticky="nsew")

        cmd = partial(self.saveSettings)
        save_Btn = Button(self, text='Save', command=cmd, background=guiColors['secondary'], foreground=guiColors['text'])
        save_Btn.grid(row=3, column=1, sticky="nsew")


    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        SettingsPage.populate(self)


# gui
class CurrentSessionPage(Page):
    explanationText = 'Tables will appear here while you are tracking. They will provide data for the current session'
    frame = None
    control_panel = None
    run_panel = None
    scrollableContainer_sub = None
    layer = 0
    split = "Wood"
    splitList1 = ['Wood', 'Iron Pickaxe', 'Nether', 'Bastion', 'Fortress', 'Nether Exit', 'Stronghold', 'End']
    splitList2 = ['Wood', 'Iron Pickaxe', 'Nether', 'Structure 1', 'Structure 2', 'Nether Exit', 'Stronghold', 'End']
    splitVars = []

    def updateTables(self, run):
        self.frame.clear_widgets()
        self.frame.add_plot_frame(currentSession['figs'][0], 0, 0, title='Splits')
        self.frame.add_plot_frame(currentSession['figs'][1], 1, 0, title='General')

        text = ''
        bastion = None
        fortress = None
        for i in range(len(self.splitList1)):
            split1 = headerLabels.index(self.splitList1[i])
            time = run[split1]
            if split1 == 'Bastion':
                try:
                    bastion = datetime.strptime(time, '%H:%M:%S.%f')
                except Exception as e:
                    print(27)
                    print(e)
            elif split1 == 'Fortress':
                try:
                    fortress = datetime.strptime(time, '%H:%M:%S.%f')
                except Exception as e:
                    print(28)
                    print(e)
                if bastion is not None and fortress is not None:
                    if self.splitVars[3].get() == 1:
                        text += (min(bastion, fortress)).strftime('%H:%M:%S.%f') + ' Structure 1    '
                    if self.splitVars[4].get() == 1:
                        text += (max(bastion, fortress)).strftime('%H:%M:%S.%f') + ' Structure 2    '
                elif bastion is not None and self.splitVars[3].get() == 1:
                    text += bastion.strftime('%H:%M:%S.%f') + ' Structure 1    '
                elif fortress is not None and self.splitVars[3].get() == 1:
                    text += fortress.strftime('%H:%M:%S.%f') + ' Structure 1    '
            elif time is not None and time != '' and self.splitVars[i].get() == 1:
                text += str(time) + ' ' + self.splitList1[i] + '    '
        if text != '':
            self.run_panel.add_label(text, self.layer, 0)
            self.layer += 1

    def populate(self):
        explanation = Label(self, text=self.explanationText, wraplength=800, foreground=guiColors['text'], font=("Arial", 14))
        explanation.grid(row=0, column=0, padx=50, columnspan=2)
        self.frame = ScrollableContainer(self)
        self.control_panel = Frame(self)

        panel_label = Label(self.control_panel, text="Runs to Display", font=("Arial", 14))
        panel_label.grid(row=0, column=0, columnspan=2, pady=5)
        Tooltip.createToolTip(panel_label, "Choose a few splits! All runs which reach the split you checked will show up")

        for i in range(len(self.splitList2)):
            self.splitVars.append(tk.IntVar())
            subFrame = Frame(self.control_panel)
            label = Label(subFrame, text=self.splitList2[i])
            check = Checkbutton(subFrame, variable=self.splitVars[i])

            label.grid(row=0, column=1)
            check.grid(row=0, column=0, padx=3)
            subFrame.grid(row=i + 1, column=0, sticky='W')


        self.run_panel = self.frame.add_scrollableContainer(0, 1, rowspan=2, height=400, width=400, xScroll=False, sticky="e")
        self.run_panel.add_title("Session Runs")

        self.frame.grid(row=1, column=1)
        self.control_panel.grid(row=1, column=0, sticky='n', padx=10, pady=10)

    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        self.populate()


class SummaryPage(Page):
    explanationText = 'Any stats, data, or figures found on this page are basic, and are more elaborate on other pages'
    frame = None
    control_panel = None

    def displayInfo(self):
        global isGraphingGeneral
        global lastRun
        if not isGraphingGeneral:
            lastRun = Stats.appendStats(settings, lastRun)
            isGraphingGeneral = True
            sessionData = Stats.getSessionData(selectedSession.get(), sessions)

            self.frame.clear_widgets()
            self.frame.add_plot_frame(Graphs.graph6(sessionData), 0, 0)
            self.frame.add_plot_frame(Graphs.graph7(sessionData), 1, 0)
            isGraphingGeneral = False


    def populate(self):
        explanation = Label(self, text=self.explanationText, wraplength=800, foreground=guiColors['text'], font=("Arial", 14))
        explanation.grid(row=0, column=0, columnspan=2, padx=50)

        self.frame = ScrollableContainer(self)
        self.frame.grid(row=1, column=1)

        self.control_panel = Frame(self)
        self.control_panel.grid(row=1, column=0, sticky='n', padx=10, pady=10)

        cmd = partial(self.displayInfo)
        graph_Btn = Button(self.control_panel, text='Graph', command=cmd, background=guiColors['secondary'], foreground=guiColors['text'])
        graph_Btn.grid(row=0, column=0, columnspan=2)

    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        SummaryPage.populate(self)


# gui
class GeneralPage(Page):
    explanationText = 'General stats, graphs, and tables will appear on this page. The most important statistics will appear on this page'
    frame = None
    control_panel = None
    rta_min = None
    rta_max = None

    def displayInfo(self):
        global isGraphingGeneral
        global lastRun
        if not isGraphingGeneral:
            lastRun = Stats.appendStats(settings, lastRun)
            isGraphingGeneral = True
            sessionData = Stats.getSessionData(selectedSession.get(), sessions)
            try:
                min1 = int(self.rta_min.get())
                max1 = int(self.rta_max.get())
                if 0 < max1 < min1:
                    raise ValueError
            except Exception as e:

                main1.errorPoppup('Make sure min and max are integers (they are in seconds)')
                return

            self.frame.clear_widgets()
            self.frame.add_plot_frame(Graphs.graph11(sessionData['general stats']), 1, 0, title='Very Important')
            self.frame.add_plot_frame(Graphs.graph12(sessionData['general stats']), 1, 1, title='Important')
            self.frame.add_plot_frame(Graphs.graph8({'Wall': sessionData['general stats']['total wall time'], 'Overworld': sessionData['general stats']['total ow time'], 'Nether': sessionData['general stats']['total nether time']}), 0, 2, title='Wall-OW-Nether breakdown')
            self.frame.add_plot_frame(Graphs.graph1(sessionData['general stats']['RTA Distribution'], 'RTA', kde=(settings['display']['use KDE'] == 1), min2=min1, max2=max1), 0, 0, title='RTA Distribution', explanation='based on RTA min and max')
            self.frame.add_plot_frame(Graphs.graph13(sessionData['general stats']['IGT Distribution'], sessionData['general stats']['latest split list']), 0, 1, title='Detailed RTA Distribution', explanation='Colors indicate the split after which the runner reset')

            isGraphingGeneral = False


    def populate(self):
        explanation = Label(self, text=self.explanationText, wraplength=800, foreground=guiColors['text'], font=("Arial", 14))
        explanation.grid(row=0, column=0, columnspan=2, padx=50)

        self.frame = ScrollableContainer(self)
        self.frame.grid(row=1, column=1)

        self.control_panel = Frame(self)
        self.control_panel.grid(row=1, column=0, sticky='n', padx=10, pady=10)

        self.rta_min = tk.StringVar()
        self.rta_max = tk.StringVar()
        self.rta_min.set('-1')
        self.rta_max.set('360')
        label1 = Label(self.control_panel, text='rta minimum')
        label2 = Label(self.control_panel, text='rta maximum')
        Tooltip.createToolTip(label1, 'left side cutoff for RTA Distribution')
        Tooltip.createToolTip(label2, 'right side cutoff for RTA Distribution')
        entry1 = Entry(self.control_panel, textvariable=self.rta_min, width=6, bg=guiColors['white'])
        entry2 = Entry(self.control_panel, textvariable=self.rta_max, width=6, bg=guiColors['white'])
        label1.grid(row=1, column=0)
        label2.grid(row=2, column=0)
        entry1.grid(row=1, column=1)
        entry2.grid(row=2, column=1)


        cmd = partial(self.displayInfo)
        graph_Btn = Button(self.control_panel, text='Graph', command=cmd, background=guiColors['secondary'], foreground=guiColors['text'])
        graph_Btn.grid(row=0, column=0, columnspan=2)

    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        GeneralPage.populate(self)


# gui
class SplitsPage(Page):
    explanationText = 'Select any split from the dropdown to set it to the active split. the graphs and tables will provide data and analysis on the active split.'
    frame = None
    control_panel = None
    selectedSplit = None
    selectedAdjustment = None
    splits = ['Iron', 'Wood', 'Iron Pickaxe', 'Nether', 'Structure 1', 'Structure 2', 'Nether Exit', 'Stronghold', 'End']

    def displayInfo(self):
        global isGraphingSplit
        global lastRun
        if not isGraphingSplit:
            lastRun = Stats.appendStats(settings, lastRun)
            isGraphingSplit = True
            sessionData = Stats.getSessionData(selectedSession.get(), sessions)

            text = f"If you reset your slowest {self.selectedAdjustment.get() * 100}% of {self.selectedSplit.get()}s, your {self.selectedSplit.get()}s per hour would decrease by no more than {self.selectedAdjustment.get() * 100}%, while your avg would decrease from {np.mean(sessionData['splits stats'][self.selectedSplit.get()]['Cumulative Distribution']):.1f} to {np.mean(Logistics.remove_top_X_percent(sessionData['splits stats'][self.selectedSplit.get()]['Cumulative Distribution'], self.selectedAdjustment.get())):.1f}"

            self.frame.clear_widgets()
            self.frame.add_plot_frame(Graphs.graph1(sessionData['splits stats'][self.selectedSplit.get()]['Cumulative Distribution'], self.selectedSplit.get(), kde=(settings['display']['use KDE'] == 1), removeX=self.selectedAdjustment.get(), smoothness=0.5), 0, 0, title="Cumulative Split Distribution")
            self.frame.add_plot_frame(Graphs.graph5(sessionData['splits stats'][self.selectedSplit.get()]), 1, 1, title='Summary')
            self.frame.add_plot_frame(Graphs.graph1(sessionData['splits stats'][self.selectedSplit.get()]['ToReset Distribution'], "Relative Reset Distribution", kde=(settings['display']['use KDE'] == 1), removeX=0, smoothness=0.5), 0, 1, title="Relative Reset Distribution", explanation="shows the distribution of time until reset with respect to the previous split")
            self.frame.add_label(text, 1, 0)


            isGraphingSplit = False

    def populate(self):
        explanation = Label(self, text=self.explanationText, wraplength=800, foreground=guiColors['text'], font=("Arial", 14))
        explanation.grid(row=0, column=0, columnspan=3, padx=50)

        self.frame = ScrollableContainer(self)
        self.frame.grid(row=1, column=1, rowspan=4)

        self.control_panel = Frame(self)
        self.control_panel.grid(row=1, column=0, sticky='n', padx=10, pady=10)

        self.selectedSplit = StringVar()
        self.selectedSplit.set("Nether")
        drop1 = OptionMenu(self.control_panel, self.selectedSplit, *self.splits)
        drop1.configure(background=guiColors['tertiary'], foreground=guiColors['text'])
        drop1.grid(row=0, column=0)

        self.selectedAdjustment = DoubleVar()
        self.selectedAdjustment.set(0.1)
        scale1 = Scale(self.control_panel, variable=self.selectedAdjustment, from_=0.0, to=0.5, orient=tk.HORIZONTAL, resolution=0.01)
        scale1.grid(row=1, column=0)

        cmd = partial(self.displayInfo)
        graph_Btn = Button(self.control_panel, text='Graph', command=cmd, background=guiColors['secondary'], foreground=guiColors['text'])
        graph_Btn.grid(row=2, column=0)

    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        SplitsPage.populate(self)


# gui
class EntryBreakdownPage(Page):
    explanationText = 'This page focusses on the overworld. It does analysis based on the different iron sources and enter types that were used to enter the nether.'
    frame = None
    control_panel = None

    def displayInfo(self):
        global isGraphingEntry
        global lastRun
        if not isGraphingEntry:
            lastRun = Stats.appendStats(settings, lastRun)
            isGraphingEntry = True
            sessionData = Stats.getSessionData(selectedSession.get(), sessions)
            enterTypeList = []
            enterMethodList = []
            for enter in sessionData['general stats']['enters']:
                enterTypeList.append(enter['type'])
                enterMethodList.append(enter['method'])

            self.frame.clear_widgets()
            self.frame.add_plot_frame(Graphs.graph4(sessionData['general stats']['enters'], settings), 0, 0, title='Heatmap')
            self.frame.add_plot_frame(Graphs.graph2(enterTypeList), 0, 1, title="Iron Source Breakdown")
            self.frame.add_plot_frame(Graphs.graph2(enterMethodList), 1, 0, title="Portal Type Breakdown")
            self.frame.add_plot_frame(Graphs.graph10(sessionData['general stats']['Exit Success']), 1, 1, title='Nether Success Breakdown')

            isGraphingEntry = False


    def populate(self):
        explanation = Label(self, text=self.explanationText, wraplength=800, foreground=guiColors['text'], font=("Arial", 14))
        explanation.grid(row=0, column=0, columnspan=2, padx=50)

        self.frame = ScrollableContainer(self)
        self.frame.grid(row=1, column=1)

        self.control_panel = Frame(self)
        self.control_panel.grid(row=1, column=0, sticky='n', padx=10, pady=10)

        cmd = partial(self.displayInfo)
        graph_Btn = Button(self.control_panel, text='Graph', command=cmd, background=guiColors['secondary'], foreground=guiColors['text'])
        graph_Btn.grid(row=1, column=0)

    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        self.populate()


# gui
class ComparisonPage(Page):
    explanationText = 'This page compares different sessions and session groups'
    frame = None
    control_panel = None


    def displayInfo(self):
        global isGraphingComparison
        global lastRun
        if not isGraphingComparison:
            lastRun = Stats.appendStats(settings, lastRun)
            isGraphingComparison = True

            self.frame.add_plot_frame(Graphs.graph9(sessions), 0, 0, title='NPH-AVG Scatterplot')

            isGraphingComparison = False

    def populate(self):
        explanation = Label(self, text=self.explanationText, wraplength=800, foreground=guiColors['text'], font=("Arial", 14))
        explanation.grid(row=0, column=0, columnspan=2, padx=50)

        self.frame = ScrollableContainer(self)
        self.frame.grid(row=1, column=1)

        self.control_panel = Frame(self)
        self.control_panel.grid(row=1, column=0, sticky='n', padx=10, pady=10)

        cmd = partial(self.displayInfo)
        graph_Btn = Button(self.control_panel, text='Graph', command=cmd, background=guiColors['secondary'], foreground=guiColors['text'])
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
        global lastRun
        if not isGivingFeedback:
            lastRun = Stats.appendStats(settings, lastRun)
            isGivingFeedback = True
            sessionData = Stats.getSessionData(selectedSession.get(), sessions)

            try:
                self.panel1.set_text("Feedback:\n" + Feedback.overworld(sessionData))
            except Exception as e:
                self.panel1.set_text('An error occured')


            try:
                self.panel2.set_text("Feedback:\n" + Feedback.nether(sessionData))
            except Exception as e:
                self.panel2.set_text('An error occured')

            isGivingFeedback = False


    def populate(self):
        explanation = Label(self, text=self.explanationText, wraplength=800, foreground=guiColors['text'], font=("Arial", 14))
        explanation.grid(row=0, column=0, columnspan=2, padx=50)

        self.container = ScrollableContainer(self)
        self.container.grid(row=1, column=1)

        self.panel1 = ScrollableTextFrame(self.container)
        self.panel1.set_header('Overworld')
        self.panel1.grid(row=0, column=0, sticky="nsew")

        self.panel2 = ScrollableTextFrame(self.container)
        self.panel2.set_header('Nether')
        self.panel2.grid(row=1, column=0, sticky="nsew")

        cmd = partial(self.displayInfo)
        graph_Btn = Button(self, text='Generate Feedback', command=cmd, background=guiColors['secondary'], foreground=guiColors['text'])
        graph_Btn.grid(row=1, column=0, sticky='n', padx=10, pady=10)

    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        self.populate()

class ExperimentPage(Page):
    explanationText = '***TESTING***'
    frame = None
    control_panel = None

    def displayInfo(self):
        global isGraphingGeneral
        global lastRun
        if not isGraphingGeneral:
            lastRun = Stats.appendStats(settings, lastRun)
            sessionData = Stats.getSessionData(selectedSession.get(), sessions)
            sessionMetaData = Stats.getSessionData(selectedSession.get(), sessions, returnMetaData=True)
            hour_list = []
            rpe_list = []
            breakTimeProportion_list = []
            x_list = []
            y_list = []
            y_list2 = []
            # Assuming you have a list of sessionmd objects called sessionmd_list

            # Find the length of the longest session
            longest_session_length = 1 + int(max([Stats.getSessionLength(session['string']) for session in sessions['sessions']]))
            # Create a 2D array of size longest_session_length by longest_session_length
            distribution_array = [[0] * (i3+1) for i3 in range(longest_session_length)]

            for i in range(len(sessions['sessions'])):


                try:
                    hour = int(sessions['sessions'][i]['string'][6:8]) + int(sessions['sessions'][i]['string'][9:11])/60
                except Exception as e:
                    pass
                else:
                    rpe = sessions['stats'][i]['general stats']['rpe']
                    breakTimeProportion = sessions['stats'][i]['general stats']['total break time']/Stats.getSessionLength(sessions['sessions'][i]['string'])/3600

                    date_time = Stats.get_column_data("Date and Time", sessions['sessions'][i])
                    nether = Stats.get_column_data("Nether", sessions['sessions'][i])
                    x_list_sub = []
                    y_list_sub = []
                    y_list_sub2 = []
                    start = datetime.strptime(date_time[0], '%Y-%m-%d %H:%M:%S.%f')
                    prev = start
                    for i2 in range(len(nether)):
                        if nether[i2] != '':
                            value = datetime.strptime(date_time[i2], '%Y-%m-%d %H:%M:%S.%f')
                            x_list_sub.append((value - start) / timedelta(seconds=1))
                            y_list_sub.append(int(nether[i2][3:5]) * 60 + int(nether[i2][6:8]))
                            y_list_sub2.append((value - prev) / timedelta(seconds=1))
                            prev = value
                    if len(x_list_sub) > 3:
                        hour_list.append(hour)
                        rpe_list.append(rpe)
                        breakTimeProportion_list.append(breakTimeProportion)
                        x_list.append(x_list_sub)
                        y_list.append(y_list_sub)

                        sessionmd = sessions['sessions'][i]
                        # Calculate the distribution using getNetherTimelineDist method
                        distribution = Stats.getNetherTimelineDist(sessionmd)

                        # Find the index of the greatest value in the distribution list
                        distribution_array[len(distribution)-1] = [x + y for x, y in zip(distribution_array[len(distribution)-1], distribution)]

                        y_list2 += y_list_sub2


            for observed_frequencies in distribution_array:
                # Calculate the expected frequencies assuming a uniform distribution
                total_observed = sum(observed_frequencies)
                num_categories = len(observed_frequencies)
                expected_frequency = total_observed / num_categories
                expected_frequencies = [expected_frequency] * num_categories

                # Perform the chi-squared goodness-of-fit test
                chi2, p_value = stats.chisquare(observed_frequencies, expected_frequencies)

            y_list2 = [item for item in y_list2 if 0 < item < 1800]

            print(y_list2)

            # Define the observed values of t
            observed_t = y_list2  # Update with your actual data

            # Define the observed value of n
            n = len(observed_t)  # Update with your actual data

            # Estimate the parameters of the gamma distribution for t
            shape, _, scale = stats.gamma.fit(observed_t, floc=0)

            # Calculate the estimated value of nph
            estimated_nph = n / np.sum(observed_t)

            # Calculate the derivative of nph with respect to the shape parameter (alpha)
            d_nph_d_alpha = -n / np.sum(observed_t) ** 2

            # Calculate the derivative of nph with respect to the scale parameter (beta)
            d_nph_d_beta = n / (np.sum(observed_t) * scale)

            # Get the estimated variance of the shape parameter (alpha)
            var_alpha = stats.gamma.fit(observed_t, floc=0)[0] / n

            # Get the estimated variance of the scale parameter (beta)
            var_beta = (stats.gamma.fit(observed_t, floc=0)[1] / scale) ** 2

            # Get the estimated covariance between the shape and scale parameters
            cov_alpha_beta = 0  # Assuming no covariance for simplicity

            # Calculate the standard error of nph using the Delta Method
            standard_error = np.sqrt((d_nph_d_alpha ** 2) * var_alpha + (
                        d_nph_d_beta ** 2) * var_beta + 2 * d_nph_d_alpha * d_nph_d_beta * cov_alpha_beta)

            # Set the desired confidence level
            confidence_level = 0.95

            # Find the critical value based on the confidence level (assuming a two-tailed test)
            critical_value = stats.norm.ppf((1 + confidence_level) / 2)

            # Calculate the confidence interval for nph
            lower_bound = (estimated_nph - critical_value * standard_error) * 3600
            upper_bound = (estimated_nph + critical_value * standard_error) * 3600

            # Print the confidence interval
            print(f"Confidence Interval for nph: ({lower_bound}, {upper_bound})")

            self.frame.clear_widgets()
            self.frame.add_plot_frame(Graphs.graph16(Stats.get_column_data("Date and Time", sessionMetaData), Stats.get_column_data("Nether", sessionMetaData)), 0, 0)
            self.frame.add_plot_frame(Graphs.graph17(x_list, y_list, hour_list, x_quantity="time of day", y_quanity="p"), 1, 0)
            self.frame.add_plot_frame(Graphs.graph17(x_list, y_list, hour_list, x_quantity="time of day", y_quanity="slope"), 1, 1)
            self.frame.add_plot_frame(Graphs.graph17(x_list, y_list, rpe_list, x_quantity="rpe", y_quanity="p"), 2, 0)
            self.frame.add_plot_frame(Graphs.graph17(x_list, y_list, rpe_list, x_quantity="rpe", y_quanity="slope"), 2, 1)
            self.frame.add_plot_frame(Graphs.graph17(x_list, y_list, breakTimeProportion_list, x_quantity="session break time", y_quanity="p"), 3, 0)
            self.frame.add_plot_frame(Graphs.graph17(x_list, y_list, breakTimeProportion_list, x_quantity="session break time", y_quanity="slope"), 3, 1)


    def populate(self):
        explanation = Label(self, text=self.explanationText, wraplength=800, foreground=guiColors['text'], font=("Arial", 14))
        explanation.grid(row=0, column=0, columnspan=2, padx=50)

        self.frame = ScrollableContainer(self)
        self.frame.grid(row=1, column=1)

        self.control_panel = Frame(self)
        self.control_panel.grid(row=1, column=0, sticky='n', padx=10, pady=10)

        cmd = partial(self.displayInfo)
        graph_Btn = Button(self.control_panel, text='Graph', command=cmd, background=guiColors['secondary'], foreground=guiColors['text'])
        graph_Btn.grid(row=0, column=0, columnspan=2)

    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        ExperimentPage.populate(self)


# gui
class MainView(Frame):
    top2 = None
    sessionMarkerInput = None
    txtFileNameInput = None
    selectedStat = None
    sessionMarkerEntry = None
    currentSessionMarkerLock = threading.Lock()
    pages = None
    trackingLabel = None
    drop = None
    pageMarker = None

    @classmethod
    def authenticateSheets(cls):
        if settings['tracking']['use sheets'] == 1:
            wks = Sheets.authenticate()
            if isinstance(wks, int):
                print('sheet link might not be correct, also make sure credentials.json is in the same folder as exe')
            return wks
        else:
            return None

    def updateCSGraphs(self, run):
        self.pages['Current Session'].updateTables(run)

    def errorPoppup(self, text):
        top = Toplevel()
        top.geometry("300x200")
        top.title("Error")
        label = Label(top, text=text, wraplength=280)
        top.grid_columnconfigure(0, weight=1)
        label.grid(row=0, column=0)

    def stopResetTracker(self):
        global isTracking
        isTracking = False
        self.trackingLabel.config(foreground=guiColors['background'])

    def startResetTracker(self):
        global isTracking
        global wks1
        wks1 = MainView.authenticateSheets()
        if not isinstance(wks1, int):
            isTracking = True
            CurrentSession.resetCurrentSession()
            self.trackingLabel.config(foreground=guiColors['black'])
            self.pages['Control'].set_button_color(False)
            t1 = threading.Thread(target=Tracking.trackResets, name="tracker")
            t1.daemon = True
            t1.start()

    @classmethod
    def startResetTracker2(cls):
        global isTracking
        global wks1
        wks1 = MainView.authenticateSheets()
        if not isinstance(wks1, int):
            t1 = threading.Thread(target=Tracking.trackResets, name="tracker2")
            t1.daemon = True
            t1.start()

    def promptUserForTracking(self):
        global currentSessionMarker
        if not isTracking:
            if not os.path.exists(settings['tracking']['records path']):
                self.errorPoppup('records path does not exists. configure/reconfigure your settings.')
                return
            top1 = Toplevel()
            top1.geometry("180x100")
            top1.title("Start Tracking")
            top1.grid_columnconfigure(0, weight=1)

            label = Label(top1, text="Enter a Session Marker")
            label.grid(row=0, column=0)

            entry = Entry(top1, bg=guiColors['white'])
            entry.grid(row=1, column=0)

            def get_value():
                global currentSessionMarker
                with self.currentSessionMarkerLock:
                    value = entry.get()
                    currentSessionMarker = value.replace('$', '')
                top1.destroy()
                self.startResetTracker()
                return value

            startTrackingButton = Button(top1, text="Start Tracking", command=get_value, background=guiColors['secondary'], foreground=guiColors['text'])
            startTrackingButton.grid(row=2, column=0)
        else:
            self.errorPoppup('Already Tracking')


    def setPage(self, name):
        self.pages[name].show()
        self.pageMarker.grid_forget()
        index = list(self.pages.keys()).index(name)
        self.pageMarker.grid(row=1, column=index)


    def __init__(self, *args, **kwargs):
        global selectedSession
        Frame.__init__(self, *args, **kwargs)
        self.pages = {
            'Control': ControlPage(self),
            'Settings': SettingsPage(self),
            'Current Session': CurrentSessionPage(self),
            'Summary': SummaryPage(self),
            'General': GeneralPage(self),
            'Splits': SplitsPage(self),
            'Entry Breakdown': EntryBreakdownPage(self),
            'Comparison': ComparisonPage(self),
            'Feedback': FeedbackPage(self),
            'Experiment': ExperimentPage(self)
        }

        self.buttonframeMain = Frame(self)
        self.buttonframe1 = Frame(self.buttonframeMain)
        self.container = Frame(self)

        self.pageMarker = Canvas(self.buttonframe1, width=30, height=3, background=guiColors['tertiary'])

        for i in range(len(self.pages)):
            pageName = list(self.pages.keys())[i]
            self.pages[pageName].place(in_=self.container, x=0, y=0, relwidth=1, relheight=1)
            command = partial(self.setPage, pageName)
            button = Button(self.buttonframe1, text=pageName, command=command, foreground=guiColors['text'], background=guiColors['primary'])
            button.grid(row=0, column=i, sticky="nsew")

        selectedSession = tk.StringVar()
        sessionStrings = []
        for session in sessions['sessions']:
            sessionStrings.append(session['string'])
        selectedSession.set(sessionStrings[0])
        self.drop = OptionMenu(self.buttonframeMain, selectedSession, *sessionStrings)
        self.drop.configure(background=guiColors['tertiary'], foreground=guiColors['text'])
        self.droplabel = Label(self.buttonframeMain, text='Session Selector: ', foreground=guiColors['tertiary'], font=("Arial Bold", 10))
        self.trackingLabel = Label(self.buttonframeMain, text='Currently Tracking', foreground=guiColors['background'], font=("Arial Bold", 10), pady=3, padx=10)
        self.trackingLabel.grid(row=0, column=3)
        self.droplabel.grid(row=0, column=0)
        self.drop.grid(row=0, column=1, padx=(0, 10))

        self.buttonframe1.grid(row=0, column=2)
        self.buttonframeMain.pack(side="top")
        self.container.pack(side="top", fill="both", expand=True)

        self.setPage("Control")




if __name__ == "__main__":
    root = tk.Tk()
    root.title('Reset Tracker')
    main1 = MainView(root)
    main1.pack(side="top", fill="both", expand=True)
    if settings['tracking']['track on launch'] == 1:
        main1.startResetTracker()
    if settings['tracking']['use sheets'] == 1:
        Stats.fixSheet(Sheets.authenticate())
    root.wm_geometry("1100x750")
    root.mainloop()
