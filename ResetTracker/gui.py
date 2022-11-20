import tkinter as tk
from tkinter import *
from functools import partial
import pygsheets
import datetime
from statistics import mean
import statistics
from statistics import quantiles
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import ImageTk, Image
import plotly.graph_objects as go
from plotly.colors import n_colors
import math
import csv
import glob
import os
from datetime import datetime, timedelta
import threading
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from typing import Optional
from ctypes import windll, create_unicode_buffer
import gspread
import json
import time
from os.path import exists
import numpy as np
import math
from scipy.stats import percentileofscore
from speedrun_models import BasicSpeedrunModel, SplitDistribution


# class methods for miscellaneous
class Logistics:

    @classmethod
    def getSettings(cls):
        with open("data/settings.json", "r") as settingsJson:
            loadedSettings = json.load(settingsJson)
            return loadedSettings

    @classmethod
    def getSessions(cls):
        with open("data/sessionData.json", "r") as sessionsJson:
            loadedSessions = json.load(sessionsJson)
            return loadedSessions

    @classmethod
    def getMean(cls, data):
        mean1 = None
        if len(data) > 0:
            mean1 = mean(data)
        return mean1

    @classmethod
    def getQuotient(cls, dividend, divisor):
        if divisor == 0:
            return None
        else:
            return dividend/divisor

    @classmethod
    def getTimezoneOffset(cls):
        if settings['display']['use local timezone'] == 1:
            return timedelta(seconds=-(time.timezone if (time.localtime().tm_isdst == 0) else time.altzone))
        else:
            return timedelta(seconds=0)

    @classmethod
    def stringToDatetime(cls, DTString):
        components = DTString.split(" ")
        links = components[0].split("/") + components[1].split(":")
        return datetime(month=int(links[0]), day=int(links[1]), year=int(links[2]), hour=int(links[3]), minute=int(links[4]), second=int(links[5]))

    @classmethod
    def stringToTimedelta(cls, TDString):
        links = TDString.split(":")
        return timedelta(hours=int(links[0]), minutes=int(links[1]), seconds=int(links[2]))

    @classmethod
    def formatValue(cls, value):
        if value is None:
            return ""
        if type(value) == str:
            return value
        if type(value) == int:
             return str(value)
        if type(value) == float:
            if value <= 1:
                return str(round(value * 100, 1)) + '%'
            else:
                return str(round(value, 1))
        if type(value) == timedelta:
            valueDatetime = datetime(year=1970, month=1, day=1) + value
            return valueDatetime.strftime("%M:%S.") + str(round(int(10 * ((value / second) % 1)), 0))

    @classmethod
    def getSessionData(cls, sessionString):
        index = 0
        for i in range(len(sessions['sessions'])):
            session = sessions['sessions'][i]
            if sessionString in session.values():
                index = i
                break
        return sessions['stats'][index]

    @classmethod
    def floatList(cls, list):
        for i in range(len(list)):
            list[i] = float(list[i])
        return list


# class methods for analyzing stats
class Stats:

    @classmethod
    def get_sessions(cls):
        sessionList = []
        sh = gc_sheets.open_by_url(settings['tracking']['sheet link'])
        wks = sh.worksheet_by_title('Raw Data')
        headers = wks.get_row(row=1, returnas='matrix', include_tailing_empty=False)

        time_col = wks.get_col(col=headers.index('Date and Time') + 1, returnas='matrix', include_tailing_empty=True)
        time_col.pop(0)
        session_col = wks.get_col(col=headers.index('Session Marker') + 1, returnas='matrix', include_tailing_empty=True)
        session_col.pop(0)
        rta_col = wks.get_col(col=headers.index('RTA') + 1, returnas='matrix', include_tailing_empty=True)
        rta_col.pop(0)
        sessionList.append({'start row': len(time_col) + 1, 'end row': 2, 'string': 'All'})

        count = 0
        session_end = 2
        end_time = Logistics.stringToDatetime(time_col[0+1]) + Logistics.stringToTimedelta(rta_col[0+1]) + Logistics.getTimezoneOffset()
        for i in range(len(session_col)):
            if session_col[i] != '':
                count += 1
                session_start = i+2
                if count == int(settings['display']['latest x sessions']):
                    sessionList.insert(1, {'start row': session_start, 'end row': 2, 'string': "Latest " + settings['display']['latest x sessions']})
                start_time = Logistics.stringToDatetime(time_col[i]) + Logistics.getTimezoneOffset()
                sessionString = start_time.strftime('%m/%d %H:%M') + " - " + end_time.strftime('%m/%d %H:%M')
                sessionList.append({'start row': session_start, 'end row': session_end, 'string': sessionString})
                session_end = i+3
                if i != len(session_col) - 1:
                    end_time = Logistics.stringToDatetime(time_col[i+1]) + Logistics.stringToTimedelta(rta_col[i+1]) + Logistics.getTimezoneOffset()
        sessionList.insert(0, {'start row': session_start, 'end row': 2, 'string': "All"})
        return sessionList


    @classmethod
    def get_stats(cls, sessionList, makeScoreKeys):

        returndict = {'splits stats': {}, 'general stats': {}}

        relativeSplitDists = {'Iron': None, 'Wood': None, 'Iron Pickaxe': None, 'Nether': [], 'Structure 1': [], 'Structure 2': [], 'Nether Exit': [], 'Stronghold': [], 'End': []}
        cumulativeSplitDists = {'Iron': [], 'Wood': [], 'Iron Pickaxe': [], 'Nether': [], 'Structure 1': [], 'Structure 2': [], 'Nether Exit': [], 'Stronghold': [], 'End': []}

        endgameDists = json.load(open('data/endgameDists.json'))

        total_RTA = 0
        total_wallResets = 0
        total_played = 0
        total_wallTime = 0
        total_owTime = 0
        entry_labels = []
        enters = []

        sh = gc_sheets.open_by_url(settings['tracking']['sheet link'])
        wks = sh.worksheet_by_title('Raw Data')

        headers = wks.get_row(row=1, returnas='matrix', include_tailing_empty=False)
        columns = {}

        for header in headers:
            temp_col = wks.get_col(col=headers.index(header) + 1, returnas='matrix', include_tailing_empty=True)
            columns[header] = []
            for session in sessionList:
                columns[header] += temp_col[session['end row']:session['start row']]

        # setting up score keys
        if makeScoreKeys:
            enterTypeOptions = ['Buried Treasure', 'Full Shipwreck', 'Half Shipwreck', 'Village']
            scoreKeys = {}
            for enterType in enterTypeOptions:
                if settings['playstyle cont.'][enterType] == 1:
                    scoreKeys[enterType] = {'data': [], 'isValid': False}
            scoreKeys['other'] = {'data': [], 'isValid': False}
            enterTypeOptions = scoreKeys.keys()

        # iterating through rows
        for row_num in range(len(columns['Date and Time'])):
            if columns['Date and Time'][row_num] != 0:
                # formatting
                rowCells = {}
                for key in columns:
                    cell = columns[key][row_num]
                    if key in ['RTA', 'Wood', 'Iron Pickaxe', 'Nether', 'Bastion', 'Fortress', 'Nether Exit', 'Stronghold', 'End', 'Iron', 'RTA Since Prev', 'Wall Time Since Prev', 'Break RTA Since Prev'] and cell != "":
                        if len(cell) == 8:
                            rowCells[key] = timedelta(hours=int(cell[0:2]), minutes=int(cell[3:5]), seconds=int(cell[6:])) / second
                        else:
                            rowCells[key] = timedelta(hours=int(cell[0]), minutes=int(cell[2:4]), seconds=int(cell[5:])) / second
                    else:
                        rowCells[key] = cell

                # resets/time
                total_RTA += rowCells['RTA'] + rowCells['RTA Since Prev']
                total_wallResets += int(rowCells['Wall Resets Since Prev'])
                total_played += int(rowCells['Played Since Prev']) + 1
                total_wallTime += int(rowCells['Wall Time Since Prev'])



                # overworld
                for split in ['Wood', 'Iron Pickaxe', 'Iron']:
                    if rowCells[split] != '':
                        cumulativeSplitDists[split].append(rowCells[split])

                # nether
                if rowCells['Nether'] != '':
                    cumulativeSplitDists['Nether'].append(rowCells['Nether'])
                    total_owTime += rowCells['Nether']
                    entry_labels.append(rowCells['Iron Source'])
                    enters.append({'time': rowCells['Nether'], 'method': rowCells['Enter Type'], 'type': rowCells['Iron Source']})

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
                            cumulativeSplitDists['Nether Exit'].append(rowCells['Nether Exit'])
                            relativeSplitDists['Nether Exit'].append(rowCells['Nether Exit'] - rowCells[st2])
                            if rowCells['Stronghold'] != '':
                                cumulativeSplitDists['Stronghold'].append(rowCells['Stronghold'])
                                relativeSplitDists['Stronghold'].append(rowCells['Stronghold'] - rowCells['Nether Exit'])
                                if rowCells['End'] != '':
                                    cumulativeSplitDists['End'].append(rowCells['End'])
                                    relativeSplitDists['End'].append(rowCells['End'] - rowCells['Stronghold'])
                    elif bast:
                        cumulativeSplitDists['Structure 1'].append(rowCells['Bastion'])
                        relativeSplitDists['Structure 1'].append(rowCells['Bastion'] - rowCells['Nether'])
                    elif fort:
                        cumulativeSplitDists['Structure 1'].append(rowCells['Fortress'])
                        relativeSplitDists['Structure 1'].append(rowCells['Fortress'] - rowCells['Nether'])
                else:
                    total_owTime += rowCells['RTA']

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
            jsonFile = open('data/scoreKeys.json', 'w')
            json.dump(scoreKeys, jsonFile)


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
                                                   'Count': len(cumulativeSplitDists[key])
                                                   }
            else:
                returndict['splits stats'][key] = {'Relative Distribution': cumulativeSplitDists[key],
                                                   'Cumulative Distribution': cumulativeSplitDists[key],
                                                   'Relative Conversion': Logistics.getQuotient(len(cumulativeSplitDists[key]), (total_wallResets + total_played)),
                                                   'Cumulative Conversion': Logistics.getQuotient(len(cumulativeSplitDists[key]), (total_wallResets + total_played)),
                                                   'Relative Average': Logistics.getMean(cumulativeSplitDists[key]),
                                                   'Cumulative Average': Logistics.getMean(cumulativeSplitDists[key]),
                                                   'Count': len(cumulativeSplitDists[key])
                                                   }
            if key in ['Nether', 'Bastion', 'Fortress', 'Nether Exit', 'Stronghold', 'End']:
                prevKey = key

        returndict['general stats'] = {'inph': Logistics.getQuotient(returndict['splits stats']['Nether']['Count'], (total_owTime)),
                                       'rnph': Logistics.getQuotient(returndict['splits stats']['Nether']['Count'], (total_owTime + total_wallTime)),
                                       'tnph': Logistics.getQuotient(returndict['splits stats']['Nether']['Count'], (total_RTA + total_wallTime)),
                                       'total RTA': total_RTA,
                                       'total resets': total_played + total_wallResets,
                                       'rpe': Logistics.getQuotient((total_wallResets + total_played), returndict['splits stats']['Nether']['Count']),
                                       'percent played': Logistics.getQuotient(total_played, total_played + total_wallResets),
                                       'average enter': returndict['splits stats']['Nether']['Cumulative Average'],
                                       'efficiency score': Stats.get_efficiencyScore(Logistics.getQuotient(returndict['splits stats']['Nether']['Count'], (total_owTime + total_wallTime)), returndict['splits stats']['Nether']['Cumulative Distribution'], entry_labels),
                                       'enters': enters
                                       }

        return returndict

    @classmethod
    def get_efficiencyScore(cls, nph, entry_distribution, entry_labels):
        return 0
        es_interval = 1
        sum = 0
        es_keys = {}
        entry_types = ['Full Shipwreck', 'Half Shipwreck', 'Buried Treasure']
        for entry_type in entry_types:
            es_keys[entry_type] = json.load(open('data/es_keys_' + entry_type[0:2]))
        for i in range(len(entry_distribution)):
            entry = entry_distribution[i]
            if 390 <= (es_interval * (math.floor((settings['playstyle']['target time'] - entry) / es_interval))) <= 600:
                sum += es_keys[entry_labels[i]][1][es_keys[entry_labels[i]][0].index(settings['playstyle']['target time'] - entry)]
        return Logistics.getQuotient(nph * sum, len(entry_distribution))

    @classmethod
    def saveSessionData(cls):
        t = threading.Thread(target=Stats.appendStats, name="sessions")
        t.daemon = True
        t.start()

    # used for saveSessionData
    @classmethod
    def appendStats(cls):
        sessionList = Stats.get_sessions()
        stats = []
        for i in range(len(sessionList)):
            if sessionList[i]['string'] == "All":
                stats.append(Stats.get_stats([sessionList[i]], True))
            else:
                stats.append(Stats.get_stats([sessionList[i]], False))
        sessionData = {'sessions': sessionList, 'stats': stats}
        with open("data/sessionData.json", "w") as sessionDataJson:
            json.dump(sessionData, sessionDataJson)
        print('done')

    @classmethod
    def uploadData(cls):
        sh = gc_sheets_database.open_by_url(databaseLink)
        careerData = Logistics.getSessionData("All")
        wks = sh[0]
        nameList = (wks.get_col(col=1, returnas='matrix', include_tailing_empty=False))
        userCount = len(nameList)
        if exists('data/name.txt'):
            nameFile = open('data/name.txt', 'r')
            name = nameFile.readline()
            nameFile.close()
        else:
            if settings['display']['upload anonymity'] == 1:
                name = "Anonymous" + str(userCount).zfill(5)
            else:
                name = settings['display']['twitch username']
            nameFile = open('data/name.txt', 'w')
            nameFile.write(name)
        values = [name, settings['playstyle']['instance count'], settings['playstyle']['target time']]
        for statistic in ['rnph', 'rpe', 'percent played', 'efficiency score']:
            values.append(careerData['general stats'][statistic])
        for statistic in ['Cumulative Average', 'Relative Average', 'Relative Conversion']:
            for split in ['Iron', 'Wood', 'Iron Pickaxe', 'Nether', 'Structure 1', 'Structure 2', 'Nether Exit', 'Stronghold', 'End']:
                values.append(careerData['splits stats'][split][statistic])
        if name in nameList:
            rownum = nameList.index(name) + 1
            wks.update_row(index=rownum, values=values, col_offset=0)
        else:
            wks.insert_rows(row=userCount, number=1, values=values, inherit=False)

    @classmethod
    def updateCurrentSession(cls, data):
        global currentSession
        if len(data) > 0:
            for rownum in range(len(data)):
                row = data[rownum]
                labels = ['RTA', 'Wood', 'Iron Pickaxe', 'Nether', 'Bastion', 'Fortress', 'Nether Exit', 'Stronghold', 'End', 'Iron', 'Wall Resets Since Prev', 'Played Since Prev', 'RTA Since Prev', 'Wall Time Since Prev']
                columnIndices = [5, 6, 7, 8, 9, 10, 11, 12, 13, 25, 26, 27, 28, 29]
                rowCells = {}
                for i in range(len(labels)):
                    if ':' in row[columnIndices[i]]:
                        rowCells[labels[i]] = Logistics.stringToTimedelta(row[columnIndices[i]])/second
                    else:
                        rowCells[labels[i]] = row[columnIndices[i]]

                # resets/time
                currentSession['general stats']['total RTA'] += rowCells['RTA'] + rowCells['RTA Since Prev']
                currentSession['general stats']['total wall resets'] += int(rowCells['Wall Resets Since Prev'])
                currentSession['general stats']['total played'] += int(rowCells['Played Since Prev']) + 1
                currentSession['general stats']['total wall time'] += int(rowCells['Wall Time Since Prev'])

                # overworld
                for split in ['Wood', 'Iron Pickaxe', 'Iron']:
                    if rowCells[split] != '':
                        currentSession['splits stats'][split]['Cumulative Sum'] += rowCells[split]
                        currentSession['splits stats'][split]['Relative Sum'] += rowCells[split]
                        currentSession['splits stats'][split]['Count'] += 1



                # nether
                if rowCells['Nether'] != '':
                    currentSession['splits stats']['Nether']['Cumulative Sum'] += rowCells['Nether']
                    currentSession['splits stats']['Nether']['Relative Sum'] += rowCells['Nether']
                    currentSession['splits stats']['Nether']['Count'] += 1
                    currentSession['general stats']['total ow time'] += rowCells['Nether']

                    bast = (rowCells['Bastion'] != '')
                    fort = (rowCells['Fortress'] != '')

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

                        if rowCells['Nether Exit'] != '':
                            currentSession['splits stats']['Nether Exit']['Cumulative Sum'] += rowCells['Nether Exit']
                            currentSession['splits stats']['Nether Exit']['Relative Sum'] += rowCells['Nether Exit'] - rowCells[st2]
                            currentSession['splits stats']['Nether Exit']['Count'] += 1
                            if rowCells['Stronghold'] != '':
                                currentSession['splits stats']['Stronghold']['Cumulative Sum'] += rowCells['Stronghold']
                                currentSession['splits stats']['Stronghold']['Relative Sum'] += rowCells['Stronghold'] - rowCells['Nether Exit']
                                currentSession['splits stats']['Stronghold']['Count'] += 1
                                if rowCells['End'] != '':
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
                    currentSession['general stats']['total RTA'] += rowCells['RTA']
                
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

        currentSession['general stats']['rnph'] = Logistics.getQuotient(currentSession['splits stats']['Nether']['Count'], currentSession['general stats']['total wall time'] + currentSession['general stats']['total ow time'])
        currentSession['general stats']['% played'] = Logistics.getQuotient(currentSession['general stats']['total played'], currentSession['general stats']['total played'] + currentSession['general stats']['total wall resets'])
        currentSession['general stats']['rpe'] = Logistics.getQuotient(1, currentSession['splits stats']['Nether']['Count'])

        Graphs.graph6()
        Graphs.graph7()


    @classmethod
    def resetCurrentSession(cls):
        global currentSession
        currentSession = {'splits stats': {}, 'general stats': {}}
        for split in ['Iron', 'Wood', 'Iron Pickaxe', 'Nether', 'Structure 1', 'Structure 2', 'Nether Exit', 'Stronghold', 'End']:
            currentSession['splits stats'][split] = {'Count': 0, 'Cumulative Sum': 0, 'Relative Sum': 0, 'Cumulative Average': None, 'Relative Average': None, 'Cumulative Conversion': None, 'Relative Conversion': None}
        currentSession['general stats'] = {'total RTA': 0, 'total wall resets': 0, 'total played': 0, 'total wall time': 0, 'total ow time': 0, 'rnph': None, '% played': None, 'rpe': None}


# class methods for creating graphs
class Graphs:
    # makes a kde histogram of a distribution of datapoints
    @classmethod
    def graph1(cls, dist, smoothness):
        data = {'dist': dist}
        sns.kdeplot(data=data, x='dist', legend=False, bw_adjust=smoothness)
        plt.savefig('data/plots/plot1.png', dpi=1000)
        plt.close()

    # makes a pie chart given a list of strings
    @classmethod
    def graph2(cls, items):
        itemsUnique = []
        itemsCount = []
        for item in items:
            if item not in itemsUnique:
                itemsUnique.append(item)
                itemsCount.append(1)
            else:
                itemsCount[itemsUnique.index(item)] += 1
        fig = plt.figure(figsize=(10, 7))
        plt.pie(itemsCount, labels=itemsUnique)
        plt.savefig('data/plots/plot2.png', dpi=1000)
        plt.close()

    # makes a table for relevant information of a split
    @classmethod
    def graph3(cls, splitStats):
        fig = go.Figure(data=[go.Table(header=dict(values=['Count', 'Average', 'Average Split', 'Conversion Rate']),
                                       cells=dict(values=[[Logistics.formatValue(splitStats['Count'])], [Logistics.formatValue(splitStats['Cumulative Average']), [Logistics.formatValue(splitStats['Relative Average'])], [Logistics.formatValue(splitStats['Relative Conversion'])]]]))
                              ])
        fig.write_image('data/plots/plot3.png')

    # makes a 2-way table showing the frequency of each combination of iron source and entry method
    @classmethod
    def graph4(cls, enters):
        ironSourceList = []
        entryMethodList = []
        validSourceList = []
        for source in ['Buried Treasure', 'Full Shipwreck', 'Half Shipwreck', 'Village']:
            if settings['playstyle cont.'][source] == 1:
                validSourceList.append(source)
        for enter in enters:
            if enter['type'] in validSourceList:
                ironSourceList.append(enter['type'])
            else:
                ironSourceList.append('Other')
            entryMethodList.append(enter['method'])
        ironSourceOptionsAll = ['Buried Treasure', 'Full Shipwreck', 'Half Shipwreck', 'Village', 'Other']
        ironSourceOptionsValid = []
        for i in range(len(ironSourceOptionsAll) - 1):
            if settings['playstyle cont.'][ironSourceOptionsAll[i]] == 1:
                ironSourceOptionsValid.append(ironSourceOptionsAll[i])
        ironSourceOptionsValid.append('other')
        entryTypeOptions = ['Magma Ravine', 'Lava Pool', 'Obsidian', 'Bucketless']
        colors = n_colors(lowcolor='rgb(255, 200, 200)', highcolor='rgb(200, 0, 0)', n_colors=len(ironSourceList) + 1, colortype='rgb')
        data = []
        fill_color = []

        for i1 in range(len(ironSourceOptionsValid)):
            data.append([])
            fill_color.append([])
            for i2 in range(len(entryTypeOptions)):
                data[i1].append(0)
                fill_color[i1].append(0)
        for i in range(len(ironSourceList)):
            ironSource = ironSourceList[i]
            entryMethod = entryMethodList[i]
            index1 = len(ironSourceOptionsValid) - 1
            if ironSource in ironSourceOptionsValid:
                index1 = ironSourceOptionsValid.index(ironSource)
            index2 = entryTypeOptions.index(entryMethod)
            data[index1][index2] += round(1/len(ironSourceList), 3)

        for i1 in range(len(fill_color)):
            for i2 in range(len(fill_color[i1])):
                fill_color[i1][i2] = colors[round(data[i1][i2] * len(ironSourceList))]

        for i1 in range(len(data)):
            for i2 in range(len(data[i1])):
                data[i1][i2] = Logistics.formatValue(data[i1][i2])

        data.insert(0, entryTypeOptions)
        fill_color.insert(0, n_colors(lowcolor='rgb(0, 200, 0)', highcolor='rgb(0, 200, 0)', n_colors=len(entryTypeOptions), colortype='rgb'))
        print('checkpoint1')
        fig = go.Figure(data=[go.Table(
            header=dict(
                values=[''] + ironSourceOptionsValid,
                line_color='white', fill_color='white',
                align='center', font=dict(color='black', size=12)
            ),
            cells=dict(
                values=data,
                line_color=fill_color,
                fill_color=fill_color,
                align='center', font=dict(color='white', size=11)
            ))
        ])
        print('checkpoint2')
        fig.write_image('data/plots/plot4.png')


    # table displaying info about a specific split
    @classmethod
    def graph5(cls, splitData):
        fig = go.Figure(data=[go.Table(
            header=dict(
                values=['Count', 'Average', 'Average Split', 'Conversion Rate'],
                line_color='white', fill_color='white',
                align='center', font=dict(color='black', size=12)
            ),
            cells=dict(
                values=[splitData['Count'], splitData['Cumulative Average'], splitData['Relative Average'], splitData['Relative Conversion']],
                line_color='blue',
                fill_color='green',
                align='center', font=dict(color='white', size=11)
            ))
        ])
        fig.write_image('data/plots/plot5.png')

    # table display split stats of current session
    @classmethod
    def graph6(cls):
        values = [['Count', 'Average', 'Average Split', 'Conversion']]
        for split in ['Iron', 'Wood', 'Iron Pickaxe', 'Nether', 'Structure 1', 'Structure 2', 'Nether Exit', 'Stronghold', 'End']:
            values.append([Logistics.formatValue(currentSession['splits stats'][split]['Count']), Logistics.formatValue(currentSession['splits stats'][split]['Cumulative Average']), Logistics.formatValue(currentSession['splits stats'][split]['Relative Average']), Logistics.formatValue(currentSession['splits stats'][split]['Relative Conversion'])])
        fig = go.Figure(data=[go.Table(
            header=dict(
                values=['', 'Iron', 'Wood', 'Iron Pickaxe', 'Nether', 'Structure 1', 'Structure 2', 'Nether Exit', 'Stronghold', 'End'],
                line_color='white', fill_color='white',
                align='center', font=dict(color='black', size=12)
            ),
            cells=dict(
                values=values,
                line_color='blue',
                fill_color='green',
                align='center', font=dict(color='white', size=11)
            ))
        ])
        fig.write_image('data/plots/plot6.png')

    # table displaying general stats of the current session
    @classmethod
    def graph7(cls):
        values = [Logistics.formatValue(currentSession['general stats']['rnph']), Logistics.formatValue(currentSession['general stats']['% played']), Logistics.formatValue(currentSession['general stats']['rpe'])]
        fig = go.Figure(data=[go.Table(
            header=dict(
                values=['rnph', '% played', 'rpe'],
                line_color='white', fill_color='white',
                align='center', font=dict(color='black', size=12)
            ),
            cells=dict(
                values=values,
                line_color='blue',
                fill_color='green',
                align='center', font=dict(color='white', size=11)
            ))
        ])
        fig.write_image('data/plots/plot7.png')

    # pie chart from dict of numerical data
    @classmethod
    def graph8(cls, data):
        fig = plt.figure(figsize=(10, 7))
        plt.pie(data.values(), labels=data.keys())
        plt.savefig('data/plots/plot8.png', dpi=1000)
        plt.close()

    # scatterplot displaying nph and average enter, with a canvas based on efficiency score
    @classmethod
    def graph9(cls):
        nph_list = []
        avg_enter_list = []
        for sessionStats in sessions['stats']:
            nph_list.append(sessionStats['general stats']['nph list'])
            avg_enter_list.append(sessionStats['splits stats']['Nether']['Cumulative Average'])

        canvas = []
        for x in range(60, 140):
            canvas.append([])
            for y in range(80, 140):
                effscore = None
                (canvas[x - 60]).append(effscore)

        dict1 = {'nph': nph_list, 'avg_enter': avg_enter_list}

        x1 = np.linspace(6, 14.0, 60)
        x2 = np.linspace(90, 150, 80)
        x, y = np.meshgrid(x1, x2)
        cm = plt.cm.get_cmap('cividis')
        fig1, ax1 = plt.subplots(figsize=(6, 4))
        p1 = plt.contourf(x, y, canvas, levels=1000)
        p2 = sns.scatterplot(x='nph', y='avg_enter', data=dict1, legend=False)
        plt.savefig("", dpi=1000)
        plt.close()


# class methods for giving feedback
class Feedback:
    @classmethod
    def splits(cls):
        sh = gc_sheets_database.open_by_url(databaseLink)
        wks = sh[0]
        nameList = (wks.get_col(col=1, returnas='matrix', include_tailing_empty=False))
        nameFile = open('data/name.txt', 'r')
        name = nameFile.readline()
        myData = wks.get_row(row=nameList.index(name) + 1, returnas='matrix', include_tailing_empty=True)
        myData = myData[7:]
        splits = ['Iron', 'Wood', 'Iron Pickaxe', 'Nether', 'Structure 1', 'Structure 2', 'Nether Exit', 'Stronghold', 'End']
        sh = gc_sheets_database.open_by_url(databaseLink)
        wks = sh[0]
        targetTimeCol = wks.get_col(col=3, returnas='matrix', include_tailing_empty=False)
        targetTimeCol.pop(0)
        similarUserList = []
        for i in range(len(targetTimeCol)):
            if -1 * int(settings['display']['comparison threshold']) < (int(targetTimeCol[i]) - int(settings['playstyle']['target time'])) < int(settings['display']['comparison threshold']):
                row = wks.get_row(row=i, returnas='matrix', include_tailing_empty=True)
                similarUserList.append(row)
        splitLists = np.transpose(np.array(similarUserList))
        splitLists = splitLists[7:]
        percentiles = {}
        for i in range(len(splitLists)):
            if i < 9:
                percentiles[splits[i % 9]] = {}
                percentiles[splits[i % 9]]["cAverage"] = percentileofscore(Logistics.floatList(splitLists[i]), myData[i])
            elif i < 18:
                percentiles[splits[i % 9]]["rAverage"] = percentileofscore(Logistics.floatList(splitLists[i]), myData[i])
            elif i < 27:
                percentiles[splits[i % 9]]["Conversion"] = percentileofscore(Logistics.floatList(splitLists[i]), myData[i])
        return percentiles

    @classmethod
    def efficiencyScore(cls):
        pass

    @classmethod
    def general(cls):
        pass


# tracking
class Sheets:
    @classmethod
    def sheets(cls):
        try:

            # Setting up constants and verifying
            gc = gspread.service_account(filename="credentials/credentials.json")
            sh = gc.open_by_url(settings['tracking']['sheet link'])
            dataSheet = sh.worksheet("Raw Data")
            color = (15.0, 15.0, 15.0)
            global pushedLines
            pushedLines = 1
            statsCsv = "stats.csv"

            def push_data():
                global pushedLines
                with open(statsCsv, newline="") as f:
                    reader = csv.reader(f)
                    data = list(reader)
                    f.close()
                Stats.updateCurrentSession(data)
                try:
                    if len(data) == 0:
                        return
                    dataSheet.insert_rows(
                        data,
                        row=2,
                        value_input_option="USER_ENTERED",
                    )
                    if pushedLines == 1:
                        endColumn = ord("A") + len(data)
                        endColumn1 = ord("A") + (endColumn // ord("A")) - 1
                        endColumn2 = ord("A") + ((endColumn - ord("A")) % 26)
                        endColumn = chr(endColumn1) + chr(endColumn2)
                        dataSheet.format(
                            "A2:" + endColumn + str(1 + len(data)),
                            {
                                "backgroundColor": {
                                    "red": color[0],
                                    "green": color[1],
                                    "blue": color[2],
                                }
                            },
                        )

                    pushedLines += len(data)
                    f = open(statsCsv, "w+")
                    f.close()



                except Exception as e:
                    print("test")
                    print(e)

            live = True
            print("Finished authorizing, will update sheet every 30 seconds")

            while live:
                push_data()
                pages[2].updateTables()
                time.sleep(30)
        except Exception as e:
            print(e)
            input("")


# tracking
class Utilities:
    @classmethod
    def getForegroundWindowTitle(cls) -> Optional[str]:
        hWnd = windll.user32.GetForegroundWindow()
        length = windll.user32.GetWindowTextLengthW(hWnd)
        buf = create_unicode_buffer(length + 1)
        windll.user32.GetWindowTextW(hWnd, buf, length + 1)

        # 1-liner alternative: return buf.value if buf.value else None
        if buf.value:
            return buf.value
        else:
            return ''

    @classmethod
    def ms_to_string(cls, ms, returnTime=False):
        if ms is None:
            return None

        ms = int(ms)

        t = datetime(1970, 1, 1) + timedelta(milliseconds=ms)
        if returnTime:
            return t
        return t.strftime("%H:%M:%S")


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
    isFirstRun = 'X'

    def __init__(self):
        self.path = None
        self.data = None

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
                # skip
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
            if 'Projector' in Utilities.getForegroundWindowTitle() or settings['playstyle']["instance count"] == "1":
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
        self.this_run[0] = Utilities.ms_to_string(self.data["final_rta"])
        for idx in range(len(advChecks)):
            # Prefer to read from timelines
            if advChecks[idx][0] == "timelines" and self.this_run[idx + 1] is None:
                for tl in self.data["timelines"]:
                    if tl["name"] == advChecks[idx][1]:
                        if lan > int(tl["rta"]):
                            self.this_run[idx + 1] = Utilities.ms_to_string(tl["igt"])
                            has_done_something = True
            # Read other stuff from advancements
            elif (advChecks[idx][0] in adv and adv[advChecks[idx][0]]["complete"] and self.this_run[idx + 1] is None):
                if lan > int(adv[advChecks[idx][0]]["criteria"][advChecks[idx][1]]["rta"]):
                    self.this_run[idx +
                                  1] = Utilities.ms_to_string(adv[advChecks[idx][0]]["criteria"][advChecks[idx][1]]["igt"])
                    has_done_something = True

        # If nothing was done, just count as reset
        if not has_done_something:
            # From earlier we know that final_rta > 0 so this is a splitless non-wall/bg reset
            self.splitless_count += 1
            # Only account for splitless RTA
            self.rta_spent += self.data["final_rta"]
            return

        # Stats
        self.this_run[len(advChecks) + 1] = Utilities.ms_to_string(
            self.data["final_igt"])
        self.this_run[len(advChecks) + 2] = Utilities.ms_to_string(
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
                "minecraft:gold_ingot" in stats["minecraft:picked_up"] or "minecraft:gold_block" in stats["minecraft:picked_up"])):
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
                    not("minecraft:crafted" in stats and ("minecraft:iron_pickaxe" in stats[
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
                        # if cooked salmon or cod eaten
                        if "minecraft:used" in stats and ("minecraft:cooked_salmon" in stats[
                                "minecraft:used"] or "minecraft:cooked_cod" in stats["minecraft:used"]):
                            iron_source = "Buried Treasure"
                        # if potato, wheat, or carrot obtained
                        elif "minecraft:recipes/food/baked_potato" in adv or (
                                "minecraft:recipes/food/bread" in adv) or (
                                "minecraft:recipes/transportation/carrot_on_a_stick" in adv):
                            iron_source = "Full Shipwreck"
                        # if sus stew or rotten flesh eaten
                        elif "minecraft:used" in stats and ("minecraft:suspicious_stew" in stats[
                                "minecraft:used"] or "minecraft:rotten_flesh" in stats["minecraft:used"]):
                            iron_source = "Full Shipwreck"
                        # if tnt exploded
                        elif "minecraft:used" in stats and "minecraft:tnt" in stats["minecraft:used"]:
                            iron_source = "Buried Treasure"
                        #if sand/gravel mined before iron acquired
                        elif "minecraft:recipes/building_blocks/magenta_concrete_powder" in adv and (
                                adv["minecraft:recipes/building_blocks/magenta_concrete_powder"]["criteria"][
                                "has_the_recipe"]["igt"] < adv["minecraft:story/smelt_iron"]["igt"]):
                            iron_source = "Buried Treasure"
                        # if wood mined before iron obtained
                        elif (("minecraft:story/smelt_iron" in adv and "minecraft:recipes/misc/charcoal" in adv) and (
                                int(adv["minecraft:story/smelt_iron"]["igt"]) > int(
                                adv["minecraft:recipes/misc/charcoal"][
                                "igt"]))) or ("minecraft:recipes/misc/charcoal" in adv and not(
                                "minecraft:story/iron_tools" in adv)):
                            if ("minecraft:custom" in stats and ("minecraft:open_chest" in stats[
                                    "minecraft:custom"] and stats["minecraft:custom"][
                                    "minecraft:open_chest"] == 1)) or ("minecraft:nether/find_bastion" in adv):
                                iron_source = "Half Shipwreck"
                            else:
                                iron_source = "Full Shipwreck"
                        else:
                            iron_source = "Half Shipwreck"

        iron_time = adv["minecraft:story/smelt_iron"]["igt"] if "minecraft:story/smelt_iron" in adv else None

        # Push to csv
        d = Utilities.ms_to_string(int(self.data["date"]), returnTime=True)
        data = ([str(d), iron_source, enter_type, gold_source, spawn_biome] + self.this_run +
                [Utilities.ms_to_string(iron_time), str(self.wall_resets), str(self.splitless_count),
                 Utilities.ms_to_string(self.rta_spent), Utilities.ms_to_string(self.break_time), Utilities.ms_to_string(self.wall_time), self.isFirstRun])
        self.isFirstRun = ''

        with open("stats.csv", "r") as infile:
            reader = list(csv.reader(infile))
            reader.insert(0, data)

        with open("stats.csv", "w", newline="") as outfile:
            writer = csv.writer(outfile)
            for line in reader:
                writer.writerow(line)
        # Reset all counters/sums
        self.wall_resets = 0
        self.rta_spent = 0
        self.splitless_count = 0
        self.wall_time = 0
        self.break_time = 0


# tracking
class Tracking:
    @classmethod
    def trackResets(cls):
        while True:
            try:
                newRecordObserver = Observer()
                event_handler = NewRecord()
                newRecordObserver.schedule(
                    event_handler, settings['tracking']["records path"], recursive=False)
                print("tracking: ", settings['tracking']["records path"])
                newRecordObserver.start()
                print("Started")
            except Exception as e:
                print("Records directory could not be found")
            else:
                break
        if settings['tracking']["delete-old-records"] == 1:
            files = glob.glob(f'{settings["tracking"]["records path"]}\\*.json')
            for f in files:
                os.remove(f)
        t = threading.Thread(
            target=Sheets.sheets, name="sheets"
        )  # < Note that I did not actually call the function, but instead sent it as a parameter
        t.daemon = True
        t.start()  # < This actually starts the thread execution in the background

        print("Tracking...")
        print("Type 'quit' when you are done")
        live = True

        try:
            while live:
                try:
                    val = input("")
                except:
                    val = ""
                if (val == "help") or (val == "?"):
                    print("there is literally one other command and it's quit")
                if (val == "stop") or (val == "quit"):
                    live = False
                time.sleep(1)
        finally:
            newRecordObserver.stop()
            newRecordObserver.join()

"""
global variables
"""

databaseLink = "https://docs.google.com/spreadsheets/d/1ky0mgYjsDE14xccw6JjmsKPrEIDHpt4TFnD2vr4Qmcc"
gc_sheets = pygsheets.authorize(service_file="credentials/credentials.json")
gc_sheets_database = pygsheets.authorize(service_file="credentials/databaseCredentials.json")
settings = Logistics.getSettings()
sessions = Logistics.getSessions()
second = timedelta(seconds=1)
currentSession = {'splits stats': {}, 'general stats': {}}
pages = []
selectedSession = None
isTracking = False
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


# gui
class Page(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)

    def show(self):
        self.lift()


# gui
class IntroPage(Page):
    def populate(self):
        pass

    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        IntroPage.populate(self)


# gui
class SettingsPage(Page):
    varStrings = [['sheet link', 'records path', 'break threshold', 'delete-old-records', 'autoupdate stats'], ['vault directory', 'twitch username', 'latest x sessions', 'comparison threshold', 'use local timezone', 'upload stats', 'upload anonymity'], ['instance count', 'target time'], ['Buried Treasure', 'Full Shipwreck', 'Half Shipwreck', 'Village']]
    varTypes = [['entry', 'entry', 'entry', 'check', 'check'], ['entry', 'entry', 'entry', 'entry', 'check', 'check', 'check'], ['entry', 'entry'], ['check', 'check', 'check', 'check']]
    varGroups = ['tracking', 'display', 'playstyle', 'playstyle cont.']
    settingsVars = []
    labels = []
    widgets = []
    containers = []
    subcontainers = []

    def saveSettings(self):
        global settings
        for i1 in range(len(self.varStrings)):
            for i2 in range(len(self.varStrings[i1])):
                settings[self.varGroups[i1]][self.varStrings[i1][i2]] = self.settingsVars[i1][i2].get()
        with open("data/settings.json", "w") as settingsJson:
            json.dump(settings, settingsJson)

    def populate(self):
        loadedSettings = Logistics.getSettings()
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
                self.subcontainers[i1][i2].pack(side="top")
        self.containers[0].grid(row=0, column=0)
        self.containers[1].grid(row=1, column=0)
        self.containers[2].grid(row=0, column=2)
        self.containers[3].grid(row=1, column=2)

        cmd = partial(self.saveSettings)
        save_Btn = tk.Button(self, text='Save', command=cmd)
        save_Btn.grid(row=2, column=1)


    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        SettingsPage.populate(self)


# gui
class CurrentSessionPage(Page):
    panel1 = None
    panel2 = None

    def updateTables(self):
        if self.panel1 is not None:
            self.panel1.grid_forget()
        img1 = Image.open("data/plots/plot6.png")
        img1 = img1.resize((600, 300), Image.LANCZOS)
        img1 = ImageTk.PhotoImage(img1)
        self.panel1 = Label(self, image=img1)
        self.panel1.image = img1
        self.panel1.grid(row=0, column=0)

        if self.panel2 is not None:
            self.panel2.grid_forget()
        img2 = Image.open("data/plots/plot7.png")
        img2 = img2.resize((600, 300), Image.LANCZOS)
        img2 = ImageTk.PhotoImage(img2)
        self.panel2 = Label(self, image=img2)
        self.panel2.image = img2
        self.panel2.grid(row=1, column=0)

    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)


# gui
class SplitsPage(Page):
    panel1 = None
    panel2 = None
    selectedSplit = None

    def displayInfo_sub(self):
        sessionData = Logistics.getSessionData(selectedSession.get())

        Graphs.graph1(sessionData['splits stats'][self.selectedSplit.get()]['Cumulative Distribution'],0.9)
        Graphs.graph5(sessionData['splits stats'][self.selectedSplit.get()])

        img1 = Image.open("data/plots/plot1.png")
        img1 = img1.resize((400, 400), Image.LANCZOS)
        img1 = ImageTk.PhotoImage(img1)
        if self.panel1 is not None:
            self.panel1.grid_forget()
        self.panel1 = Label(self, image=img1)
        self.panel1.image = img1
        self.panel1.grid(row=0, column=1)


        img2 = Image.open("data/plots/plot5.png")
        img2 = img2.resize((400, 200), Image.LANCZOS)
        img2 = ImageTk.PhotoImage(img2)
        if self.panel2 is not None:
            self.panel2.grid_forget()
        self.panel2 = Label(self, image=img2)
        self.panel2.image = img2
        self.panel2.grid(row=1, column=1)

    def displayInfo(self):
        t1 = threading.Thread(
            target=self.displayInfo_sub, name="graph5"
        )
        t1.daemon = True
        t1.start()

    def populate(self):
        splits = ['Wood', 'Iron Pickaxe', 'Nether', 'Structure 1', 'Structure 2', 'Nether Exit', 'Stronghold', 'End', 'Iron']
        self.selectedSplit = StringVar()
        self.selectedSplit.set("Nether")
        drop1 = OptionMenu(self, self.selectedSplit, *splits)
        drop1.grid(row=0, column=0)
        cmd = partial(self.displayInfo)
        graph_Btn = tk.Button(self, text='Graph', command=cmd)
        graph_Btn.grid(row=1, column=0)

    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        SplitsPage.populate(self)


# gui
class EntryBreakdownPage(Page):
    panel1 = None
    panel2 = None

    def displayInfo_sub(self):
        sessionData = Logistics.getSessionData(selectedSession.get())
        Graphs.graph4(sessionData['general stats']['enters'])
        img = Image.open("data/plots/plot4.png")
        img = img.crop((30, 80, 670, 280))
        img = ImageTk.PhotoImage(img)
        print('checkpoint 3')
        if self.panel1 is not None:
            self.panel1.grid_forget()
        self.panel1 = Label(self, image=img)
        self.panel1.image = img
        self.panel1.grid(row=1, column=0)

    def displayInfo(self):
        cmd = partial(self.displayInfo_sub)
        t1 = threading.Thread(
            target=cmd, name="graph4"
        )
        t1.daemon = True
        t1.start()

    def populate(self):
        cmd = partial(self.displayInfo)
        graph_Btn = tk.Button(self, text='Graph', command=cmd)
        graph_Btn.grid(row=0, column=0)

    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        EntryBreakdownPage.populate(self)


# gui
class SpawnImagePage(Page):
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)


# gui
class CompareSessionsPage(Page):
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)


# gui
class MainView(tk.Frame):

    def startResetTracker(self):
        global isTracking
        isTracking = True
        Stats.resetCurrentSession()
        t1 = threading.Thread(
            target=Tracking.trackResets, name="tracker"
        )  # < Note that I did not actually call the function, but instead sent it as a parameter
        t1.daemon = True
        t1.start()  # < This actually starts the thread execution in the background

    def __init__(self, *args, **kwargs):
        global pages
        global selectedSession
        tk.Frame.__init__(self, *args, **kwargs)
        pageTitles = ['About', 'Settings', 'Current Session', 'Splits', 'Entry Breakdown', 'Spawn Image', 'Session Comparison']
        pages = [IntroPage(self), SettingsPage(self), CurrentSessionPage(self), SplitsPage(self), EntryBreakdownPage(self), SpawnImagePage(self), CompareSessionsPage(self)]

        buttonframe1 = tk.Frame(self)
        buttonframe2 = tk.Frame(self)
        container = tk.Frame(self)

        buttonframe1.pack(side="top", fill="x", expand=False)
        buttonframe2.pack(side="bottom", fill="x", expand=False)
        container.pack(side="top", fill="both", expand=True)

        for i in range(len(pages)):
            pages[i].place(in_=container, x=0, y=0, relwidth=1, relheight=1)
            button = tk.Button(buttonframe1, text=pageTitles[i], command=pages[i].show)
            button.grid(row=0, column=i)

        pages[0].show()



        selectedSession = tk.StringVar()
        sessionStrings = []
        for session in sessions['sessions']:
            sessionStrings.append(session['string'])
        selectedSession.set(sessionStrings[0])
        drop = OptionMenu(buttonframe2, selectedSession, *sessionStrings)

        startTracker_Btn = tk.Button(buttonframe2, text="start tracking", command=self.startResetTracker)
        updateData_Btn = tk.Button(buttonframe2, text="update stats", command=Stats.saveSessionData)
        uploadData_Btn = tk.Button(buttonframe2, text="upload stats", command=Stats.uploadData)

        drop.grid(row=0, column=0)
        startTracker_Btn.grid(row=0, column=1)
        updateData_Btn.grid(row=0, column=2)
        uploadData_Btn.grid(row=0, column=3)


if __name__ == "__main__":
    root = tk.Tk()
    main = MainView(root)
    main.pack(side="top", fill="both", expand=True)
    root.wm_geometry("1200x700")
    root.mainloop()
