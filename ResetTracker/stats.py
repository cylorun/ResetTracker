from speedrun_models import SplitDistribution
from utils import *

headerLabels = ['Date and Time', 'Iron Source', 'Enter Type', 'Gold Source', 'Spawn Biome', 'RTA', 'Wood',
                'Iron Pickaxe', 'Nether', 'Bastion', 'Fortress', 'Nether Exit', 'Stronghold', 'End', 'Retimed IGT',
                'IGT', 'Gold Dropped', 'Blaze Rods', 'Blazes', 'Diamond Pick', 'Pearls Thrown', 'Deaths',
                'Obsidian Placed', 'Diamond Sword', 'Blocks Mined', 'Iron', 'Wall Resets Since Prev',
                'Played Since Prev', 'RTA Since Prev', 'Break RTA Since Prev', 'Wall Time Since Prev', 'Session Marker',
                'RTA Distribution']


class Stats:
    @classmethod
    def get_last_time(cls):
        with open('stats.csv', 'r') as file:
            csv_reader = csv.reader(file)
            last_line = None
            try:
                for row in csv_reader:
                    last_line = row
                return last_line[0]
            except Exception as e:
                return None


    @classmethod
    def getSessionData(cls, sessionString, sessions, returnMetaData=False):
        index = 0
        for i in range(len(sessions['sessions'])):
            session = sessions['sessions'][i]
            if sessionString in session.values():
                index = i
                break
        if returnMetaData:
            return sessions['sessions'][index]
        else:
            return sessions['stats'][index]

    @classmethod
    def get_sessions(cls, settings):
        with open('stats.csv', newline="") as f:
            reader = csv.reader(f)
            data = list(reader)
            f.close()

        data = data[::-1]

        sessionList = []
        profiles = {}

        final = None

        time_col = list((np.transpose(data))[headerLabels.index('Date and Time')])
        session_col = list((np.transpose(data))[headerLabels.index('Session Marker')])
        rta_col = list((np.transpose(data))[headerLabels.index('RTA')])

        count = 0
        session_end = 1

        timezoneOffset = Logistics.getTimezoneOffset(settings)

        end_time = datetime.strptime(time_col[0], '%Y-%m-%d %H:%M:%S.%f') + Logistics.stringToTimedelta(rta_col[0]) + timezoneOffset
        for i in range(len(session_col)):
            if session_col[i] != '':
                count += 1
                session_start = i
                if count == int(settings['display']['latest x sessions']):
                    sessionList.insert(0, {'start row': [session_start + 1], 'end row': [1], 'string': "Latest " + settings['display']['latest x sessions'], 'profile': None, 'version': None})
                start_time = datetime.strptime(time_col[i], '%Y-%m-%d %H:%M:%S.%f') + timezoneOffset
                sessionString = start_time.strftime('%m/%d/%Y %H:%M') + " - " + end_time.strftime('%m/%d/%Y %H:%M')
                profile = (session_col[i].split('$'))[0]
                version = (session_col[i].split('$'))[1]
                sessionList.append({'start row': [session_start + 1], 'end row': [session_end], 'string': sessionString, 'profile': profile, 'version': version})
                if profile in profiles.keys():
                    profiles[profile]['start row'].append(session_start + 1)
                    profiles[profile]['end row'].append(session_end)
                else:
                    profiles[profile] = {'start row': [session_start + 1], 'end row': [session_end], 'string': profile, 'profile': profile, 'version': version}
                session_end = i + 1
                if i != len(session_col) - 1 and time_col[i+1] != '':
                    end_time = datetime.strptime(time_col[i+1], '%Y-%m-%d %H:%M:%S.%f') + Logistics.stringToTimedelta(rta_col[i+1]) + timezoneOffset
        try:
            sessionList.insert(0, {'start row': [session_start + 1], 'end row': [1], 'string': "All", 'profile': None, 'version': None})
        except:
            return []
        return sessionList

    @classmethod
    def get_column_data(cls, column_name, session_element):
        with open('stats.csv', newline="") as f:
            reader = csv.reader(f)
            data = list(reader)
            f.close()

        start_row = session_element['start row'][0]
        end_row = session_element['end row'][0]

        column_index = headerLabels.index(column_name)  # Assuming column names are in the first row
        if end_row == 1:
            column_data = [row[column_index] for row in data[-start_row:]]
        else:
            column_data = [row[column_index] for row in data[-start_row:-end_row]]

        return column_data

    @classmethod
    def getSessionLength(cls, string):
        try:
            return (datetime.strptime(string[-16:], '%m/%d/%Y %H:%M') - datetime.strptime(string[:16], '%m/%d/%Y %H:%M'))/timedelta(hours=1)
        except Exception as e:
            print(e, 'a')
            return -1


    @classmethod
    def getNetherTimelineDist(cls, sessionMD):
        dt = Stats.get_column_data("Date and Time", sessionMD)
        nether = Stats.get_column_data("Nether", sessionMD)
        n = 1 + int(Stats.getSessionLength(sessionMD['string']))
        if n == -1:
            return -1
        start = datetime.strptime(dt[0], '%Y-%m-%d %H:%M:%S.%f')
        dist = n * [0]
        for i in range(len(nether)):
            if nether[i] != '':
                hour_num = int((datetime.strptime(dt[i], '%Y-%m-%d %H:%M:%S.%f') - start) / timedelta(hours=1))
                dist[hour_num] += 1
        return dist

    @classmethod
    def get_stats(cls, session, makeScoreKeys, settings):
        returndict = {'splits stats': {}, 'general stats': {}}

        relativeSplitDists = {'Iron': None, 'Wood': None, 'Iron Pickaxe': None, 'Nether': [], 'Structure 1': [], 'Structure 2': [], 'Nether Exit': [], 'Stronghold': [], 'End': []}
        cumulativeSplitDists = {'Iron': [], 'Wood': [], 'Iron Pickaxe': [], 'Nether': [], 'Structure 1': [], 'Structure 2': [], 'Nether Exit': [], 'Stronghold': [], 'End': []}
        toResetDists = {'Iron': [], 'Wood': [], 'Iron Pickaxe': [], 'Nether': [], 'Structure 1': [],
                                'Structure 2': [], 'Nether Exit': [], 'Stronghold': [], 'End': []}

        endgameDistsJson = open('data/endgameDists.json')
        endgameDists = json.load(endgameDistsJson)
        endgameDistsJson.close()

        total_RTA = 0
        total_wallResets = 0
        total_played = 0
        total_wallTime = 0
        total_owTime = 0
        total_break_RTA = 0
        breakCount = 0
        entry_labels = []
        enters = []
        latestSplitList = []
        igtDist = []
        exitSuccess = {}
        rtaDist = []
        ironSourceDist = {}

        with open('stats.csv', newline="") as f:
            reader = csv.reader(f)
            allData = list(reader)
            f.close()
        allData = allData[::-1]
        data = []

        for i in range(len(session['start row'])):
            data += allData[(session['end row'][i]):(session['start row'][i])]

        # setting up score keys
        if makeScoreKeys:
            enterTypeOptions = ['Buried Treasure w/ tnt', 'Buried Treasure', 'Full Shipwreck', 'Half Shipwreck', 'Village']
            scoreKeys = {}
            for enterType in enterTypeOptions:
                if settings['playstyle cont.'][enterType] == 1:
                    scoreKeys[enterType] = {'data': [], 'isValid': False}
            scoreKeys['other'] = {'data': [], 'isValid': False}
            enterTypeOptions = scoreKeys.keys()

        for item in ['Buried Treasure w/ tnt', 'Buried Treasure', 'Full Shipwreck', 'Half Shipwreck', 'Village']:
            if settings['playstyle cont.'][item] == 1:
                exitSuccess[item] = {'Iron Count': 0, 'Wood Count': 0, 'Enter Count': 0, 'Exit Count': 0, 'Wood Conversion': None, 'Enter Conversion': None, 'Exit Conversion': None, 'Sum Iron': 0, 'Average Iron': None, 'Sum Enter': 0, 'Average Enter': None, 'Sum Split': 0, 'Average Split': None}
        exitSuccess['other'] = {'Iron Count': 0, 'Wood Count': 0, 'Enter Count': 0, 'Exit Count': 0, 'Wood Conversion': None, 'Enter Conversion': None, 'Exit Conversion': None, 'Sum Iron': 0, 'Average Iron': None, 'Sum Enter': 0, 'Average Enter': None, 'Sum Split': 0, 'Average Split': None}

        # iterating through rows
        for row_num in range(len(data) - 1):
            if data[row_num][0] != '':
                # formatting
                rowCells = {}
                for key in headerLabels:
                    cell = data[row_num][headerLabels.index(key)]
                    if key in ['RTA', 'Wood', 'Iron Pickaxe', 'Nether', 'Bastion', 'Fortress', 'Nether Exit', 'Stronghold', 'End', 'Iron', 'IGT', 'RTA Since Prev', 'Wall Time Since Prev', 'Break RTA Since Prev'] and cell != "":
                        if len(cell) == 8:
                            rowCells[key] = timedelta(hours=int(cell[0:2]), minutes=int(cell[3:5]), seconds=int(cell[6:])) / timedelta(seconds=1)
                        else:
                            rowCells[key] = timedelta(hours=int(cell[0]), minutes=int(cell[2:4]), seconds=int(cell[5:])) / timedelta(seconds=1)
                    elif key == 'RTA Distribution':
                        if cell == '':
                            rowCells[key] = []
                        elif '$' not in cell:
                            rowCells[key] = [cell]
                        else:
                            rowCells[key] = cell.split('$')
                        for i in range(len(rowCells[key])):
                            rowCells[key][i] = int(rowCells[key][i])
                    else:
                        rowCells[key] = cell


                # resets/time
                total_RTA += rowCells['RTA'] + rowCells['RTA Since Prev'] + rowCells['Wall Time Since Prev']
                total_wallResets += int(rowCells['Wall Resets Since Prev'])
                total_played += int(rowCells['Played Since Prev']) + 1
                total_wallTime += int(rowCells['Wall Time Since Prev'])
                total_break_RTA += rowCells['Break RTA Since Prev']
                if rowCells['Break RTA Since Prev'] > 0:
                    breakCount += 1
                latestSplit = 'None'

                if rowCells['Iron Source'] != 'None':
                    if rowCells['Iron Source'] not in ironSourceDist.keys():
                        ironSourceDist[rowCells['Iron Source']] = 1
                    else:
                        ironSourceDist[rowCells['Iron Source']] += 1

                # overworld
                for split in ['Iron', 'Wood', 'Iron Pickaxe']:
                    if rowCells[split] != '':
                        latestSplit = split
                        cumulativeSplitDists[split].append(rowCells[split])

                if rowCells['Iron'] != '':
                    if rowCells['Iron Source'] in exitSuccess.keys():
                        exitSuccess[rowCells['Iron Source']]['Iron Count'] += 1
                        exitSuccess[rowCells['Iron Source']]['Sum Iron'] += rowCells['Iron']
                        if rowCells['Wood'] != '':
                            exitSuccess[rowCells['Iron Source']]['Wood Count'] += 1

                    elif rowCells['Iron Source'] != 'None':
                        exitSuccess['other']['Iron Count'] += 1
                        exitSuccess['other']['Sum Iron'] += rowCells['Iron']
                        if rowCells['Wood'] != '':
                            exitSuccess['other']['Wood Count'] += 1

                # nether
                if rowCells['Nether'] != '':
                    latestSplit = 'Nether'
                    cumulativeSplitDists['Nether'].append(rowCells['Nether'])
                    total_owTime += rowCells['Nether']
                    entry_labels.append(rowCells['Iron Source'])
                    enters.append({'time': rowCells['Nether'], 'method': rowCells['Enter Type'], 'type': rowCells['Iron Source']})
                    if rowCells['Iron Source'] in exitSuccess.keys():
                        exitSuccess[rowCells['Iron Source']]['Enter Count'] += 1
                        exitSuccess[rowCells['Iron Source']]['Sum Enter'] += rowCells['Nether']
                    else:
                        exitSuccess['other']['Enter Count'] += 1
                        exitSuccess['other']['Sum Enter'] += rowCells['Nether']

                    if makeScoreKeys:
                        if rowCells['Stronghold'] != '':

                            if rowCells['Iron Source'] in enterTypeOptions:
                                scoreKeys[rowCells['Iron Source']]['data'].append((rowCells['Stronghold'] - rowCells['Nether']))
                                scoreKeys[rowCells['Iron Source']]['isValid'] = True
                            else:
                                scoreKeys['other']['data'].append((rowCells['Stronghold'] - rowCells['Nether']))
                                scoreKeys['other']['isValid'] = True
                        else:
                            if rowCells['Iron Source'] in enterTypeOptions:
                                scoreKeys[rowCells['Iron Source']]['data'].append('run kill')
                            else:
                                scoreKeys['other']['data'].append('run kill')

                    bast = (rowCells['Bastion'] != '')
                    fort = (rowCells['Fortress'] != '')

                    if fort and bast:
                        latestSplit = 'Structure 2'
                        fortFirst = (rowCells['Bastion'] > rowCells['Fortress'])
                        st1 = 'Bastion'
                        st2 = 'Fortress'
                        if fortFirst:
                            st1 = 'Fortress'
                            st2 = 'Bastion'
                        cumulativeSplitDists['Structure 1'].append(rowCells[st1])
                        cumulativeSplitDists['Structure 2'].append(rowCells[st2])
                        relativeSplitDists['Structure 1'].append(rowCells[st1] - rowCells['Nether'])
                        relativeSplitDists['Structure 2'].append(rowCells[st2] - rowCells[st1])

                        if rowCells['Nether Exit'] != '':
                            latestSplit = 'Nether Exit'
                            cumulativeSplitDists['Nether Exit'].append(rowCells['Nether Exit'])
                            relativeSplitDists['Nether Exit'].append(rowCells['Nether Exit'] - rowCells[st2])
                            if rowCells['Iron Source'] in exitSuccess.keys():
                                exitSuccess[rowCells['Iron Source']]['Exit Count'] += 1
                                exitSuccess[rowCells['Iron Source']]['Sum Split'] += rowCells['Nether Exit'] - rowCells['Nether']
                            else:
                                exitSuccess['other']['Exit Count'] += 1
                                exitSuccess['other']['Sum Split'] += rowCells['Nether Exit'] - rowCells['Nether']
                            if rowCells['Stronghold'] != '':
                                latestSplit = 'Stronghold'
                                cumulativeSplitDists['Stronghold'].append(rowCells['Stronghold'])
                                relativeSplitDists['Stronghold'].append(rowCells['Stronghold'] - rowCells['Nether Exit'])
                                if rowCells['End'] != '':
                                    latestSplit = 'End'
                                    cumulativeSplitDists['End'].append(rowCells['End'])
                                    relativeSplitDists['End'].append(rowCells['End'] - rowCells['Stronghold'])
                    elif bast:
                        st1 = 'Bastion'
                        latestSplit = 'Structure 1'
                        cumulativeSplitDists['Structure 1'].append(rowCells['Bastion'])
                        relativeSplitDists['Structure 1'].append(rowCells['Bastion'] - rowCells['Nether'])
                    elif fort:
                        st1 = 'Fortress'
                        latestSplit = 'Structure 1'
                        cumulativeSplitDists['Structure 1'].append(rowCells['Fortress'])
                        relativeSplitDists['Structure 1'].append(rowCells['Fortress'] - rowCells['Nether'])
                else:
                    total_owTime += rowCells['RTA']


                rtaDist += (rowCells['RTA Distribution'])
                igts = (rowCells['RTA Distribution'])
                igts[len(igts) - 1] = rowCells['IGT']
                igtDist += igts
                latestSplits = ['None'] * (len(rowCells['RTA Distribution']) - 1)
                latestSplitList += (latestSplits + [latestSplit])

                if latestSplit == 'Structure 1':
                    toResetDists[latestSplit].append(rowCells['IGT'] - rowCells[st1])
                elif latestSplit == 'Structure 2':
                    toResetDists[latestSplit].append(rowCells['IGT'] - rowCells[st2])
                else:
                    toResetDists[latestSplit].append(rowCells['IGT'] - rowCells[latestSplit])

        # making/updating scoreKeys
        if makeScoreKeys:
            for key in scoreKeys.keys():
                if scoreKeys[key]['isValid']:
                    splitDist = SplitDistribution.from_data(scoreKeys[key]['data'], 1)
                    splitDist.convolve(SplitDistribution.from_data(endgameDists['Stronghold'], 1))
                    splitDist.convolve(SplitDistribution.from_data(endgameDists['End'], 1))
                    scoreKeys[key]['dist'] = splitDist.to_data()
                else:
                    scoreKeys[key]['dist'] = None
            scoreKeysFile = open('data/scoreKeys.json', 'w')
            json.dump(scoreKeys, scoreKeysFile)
            scoreKeysFile.close()

        # updating exitSuccess
        for key in exitSuccess.keys():
            exitSuccess[key]['Exit Conversion'] = Logistics.getQuotient(exitSuccess[key]['Exit Count'], exitSuccess[key]['Enter Count'])
            exitSuccess[key]['Enter Conversion'] = Logistics.getQuotient(exitSuccess[key]['Enter Count'], exitSuccess[key]['Iron Count'])
            exitSuccess[key]['Wood Conversion'] = Logistics.getQuotient(exitSuccess[key]['Wood Count'], exitSuccess[key]['Iron Count'])
            exitSuccess[key]['Average Iron'] = Logistics.getQuotient(exitSuccess[key]['Sum Iron'], exitSuccess[key]['Iron Count'])
            exitSuccess[key]['Average Enter'] = Logistics.getQuotient(exitSuccess[key]['Sum Enter'], exitSuccess[key]['Enter Count'])
            exitSuccess[key]['Average Split'] = Logistics.getQuotient(exitSuccess[key]['Sum Split'], exitSuccess[key]['Exit Count'])

        # preparing returndict
        prevKey = None
        for key in ['Iron', 'Wood', 'Iron Pickaxe', 'Nether', 'Structure 1', 'Structure 2', 'Nether Exit', 'Stronghold', 'End']:
            if prevKey is not None:
                returndict['splits stats'][key] = {'Relative Distribution': relativeSplitDists[key],
                                                   'Cumulative Distribution': cumulativeSplitDists[key],
                                                   'Relative Conversion': Logistics.getQuotient(len(cumulativeSplitDists[key]), len(cumulativeSplitDists[prevKey])),
                                                   'Cumulative Conversion': Logistics.getQuotient(len(cumulativeSplitDists[key]), (total_wallResets + total_played)),
                                                   'Relative Average': Logistics.getMean(relativeSplitDists[key]),
                                                   'Cumulative Average': Logistics.getMean(cumulativeSplitDists[key]),
                                                   'Relative Stdev': Logistics.getStdev(relativeSplitDists[key]),
                                                   'Cumulative Stdev': Logistics.getStdev(cumulativeSplitDists[key]),
                                                   'Count': len(cumulativeSplitDists[key]),
                                                   'ToReset Distribution': toResetDists[key]
                                                   }
            else:
                returndict['splits stats'][key] = {'Relative Distribution': cumulativeSplitDists[key],
                                                   'Cumulative Distribution': cumulativeSplitDists[key],
                                                   'Relative Conversion': Logistics.getQuotient(len(cumulativeSplitDists[key]), (total_wallResets + total_played)),
                                                   'Cumulative Conversion': Logistics.getQuotient(len(cumulativeSplitDists[key]), (total_wallResets + total_played)),
                                                   'Relative Average': Logistics.getMean(cumulativeSplitDists[key]),
                                                   'Cumulative Average': Logistics.getMean(cumulativeSplitDists[key]),
                                                   'Relative Stdev': Logistics.getStdev(cumulativeSplitDists[key]),
                                                   'Cumulative Stdev': Logistics.getStdev(cumulativeSplitDists[key]),
                                                   'Count': len(cumulativeSplitDists[key]),
                                                   'ToReset Distribution': toResetDists[key]
                                                   }
            if key in ['Iron', 'Wood', 'Iron Pickaxe', 'Nether']:
                returndict['splits stats'][key]['xph'] = Logistics.getQuotient(Logistics.getQuotient(returndict['splits stats'][key]['Count'], (total_owTime + total_wallTime)), 1/3600)
            else:
                returndict['splits stats'][key]['xph'] = Logistics.getQuotient(Logistics.getQuotient(returndict['splits stats'][key]['Count'], (total_RTA + total_wallTime)), 1/3600)
            if key in ['Nether', 'Bastion', 'Fortress', 'Nether Exit', 'Stronghold', 'End']:
                prevKey = key

        returndict['general stats'] = {'rnph': Logistics.getQuotient(Logistics.getQuotient(returndict['splits stats']['Nether']['Count'], (total_owTime + total_wallTime)), 1/3600),
                                       'total time': total_RTA,
                                       'total Walltime': total_wallTime,
                                       'total ow time': total_owTime,
                                       'total nether time': total_RTA - total_owTime,
                                       'total break time': total_break_RTA,
                                       'break count': breakCount,
                                       'total resets': total_played + total_wallResets,
                                       'rpe': Logistics.getQuotient((total_wallResets + total_played), returndict['splits stats']['Nether']['Count']),
                                       'percent played': Logistics.getQuotient(len(rtaDist), total_played + total_wallResets),
                                       'average enter': returndict['splits stats']['Nether']['Cumulative Average'],
                                       'efficiency score': Stats.get_efficiencyScore(Logistics.getQuotient(returndict['splits stats']['Nether']['Count'], (total_owTime + total_wallTime)), enters, settings),
                                       'Iron Source Dist': ironSourceDist,
                                       'enters': enters,
                                       'Exit Success': exitSuccess,
                                       'RTA Distribution': rtaDist,
                                       'IGT Distribution': igtDist,
                                       'latest split list': latestSplitList
                                       }
        returndict['profile'] = session['profile']

        return returndict

    @classmethod
    def get_efficiencyScore(cls, nph, enters, settings):
        sum = 0
        validEnterTypes = ['other']
        enterTypes = ['Buried Treasure w/ tnt', 'Buried Treasure', 'Full Shipwreck', 'Half Shipwreck', 'Village']
        scoreKeysFile = open('data/scoreKeys.json', 'r')
        scoreKeys = json.load(scoreKeysFile)
        scoreKeysFile.close()
        for enterType in enterTypes:
            if settings['playstyle cont.'][enterType] == 1:
                validEnterTypes.insert(0, enterType)
        for enter in enters:
            if enter['type'] in validEnterTypes:
                enterType = enter['type']
            else:
                enterType = 'other'
            if scoreKeys[enterType]['isValid']:
                postEnterMax = int(settings['playstyle']['target time']) - enter['time']
                index = int(((postEnterMax) - scoreKeys[enterType]['dist']['start split'])/scoreKeys[enterType]['dist']['split step'])
                if index >= 0:
                    sum += scoreKeys[enterType]['dist']['probabilities'][index]
        if nph is None:
            return 0
        return Logistics.getQuotient(nph * sum, len(enters))

    @classmethod
    def saveSessionData(cls, settings):
        command = partial(Stats.appendStats, settings)
        t = threading.Thread(target=command, name="sessions")
        t.daemon = False
        t.start()

    # used for saveSessionData
    @classmethod
    def appendStats(cls, settings, last):
        global sessions
        new_last = Stats.get_last_time()
        if new_last is not None and (last is None or new_last != last):
            sessionList = Stats.get_sessions(settings)
            if len(sessionList) == 0:
                return None
            stats = []
            for i in range(len(sessionList)):
                if sessionList[i]['string'] == "All":
                    stats.append(Stats.get_stats(sessionList[i], True, settings))
                else:
                    stats.append(Stats.get_stats(sessionList[i], False, settings))
            sessions = {'sessions': sessionList, 'stats': stats}
            with open("data/sessionData.json", "w") as sessionDataJson:
                json.dump(sessions, sessionDataJson)
            sessionDataJson.close()
        return new_last


