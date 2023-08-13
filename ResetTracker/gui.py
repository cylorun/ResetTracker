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

from stats import *


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
    def openGithub(cls):
        webbrowser.open_new_tab('https://github.com/pncakespoon1/ResetTracker')


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
            print('sheet link might not be correct, also make sure credentials.json is in the same folder as exe')
            return None
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
        self.isFirstRun = '$' + config['version']

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
        self.isFirstRun = '$' + config['version']


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
class MainView(Frame):
    @classmethod
    def authenticateSheets(cls):
        if settings['tracking']['use sheets'] == 1:
            wks = Sheets.authenticate()
            if isinstance(wks, int):
                print('sheet link might not be correct, also make sure credentials.json is in the same folder as exe')
            return wks
        else:
            return None

    def startResetTracker(self):
        global wks1
        wks1 = MainView.authenticateSheets()
        if not isinstance(wks1, int):
            CurrentSession.resetCurrentSession()
            t1 = threading.Thread(target=Tracking.trackResets, name="tracker")
            t1.daemon = True
            t1.start()

    @classmethod
    def startResetTracker2(cls):
        global wks1
        wks1 = MainView.authenticateSheets()
        if not isinstance(wks1, int):
            t1 = threading.Thread(target=Tracking.trackResets, name="tracker2")
            t1.daemon = True
            t1.start()


if __name__ == "__main__":
    main1.startResetTracker()

