from statistics import mean, stdev, median
import numpy as np
import datetime
from datetime import datetime, timedelta
import json
from datetime import time
from typing import Optional
from ctypes import windll, create_unicode_buffer
import time
import math
import sqlite3



class FileLoader:
    @classmethod
    def getConfig(cls):
        configJson = open("data/config.json", "r")
        loadedConfig = json.load(configJson)
        configJson.close()
        return loadedConfig

    @classmethod
    def getSettings(cls):
        settingsJson = open("data/settings.json", "r")
        loadedSettings = json.load(settingsJson)
        settingsJson.close()
        return loadedSettings

    @classmethod
    def getSessions(cls):
        sessionsJson = open("data/sessionData.json", "r")
        loadedSessions = json.load(sessionsJson)
        sessionsJson.close()
        return loadedSessions

    @classmethod
    def getThresholds(cls):
        thresholdsJson = open("data/thresholds.json", "r")
        loadedThresholds = json.load(thresholdsJson)
        thresholdsJson.close()
        return loadedThresholds


class Logistics:
    @classmethod
    def get_previous_item(cls, lst, item):
        index = lst.index(item)
        if index > 0:
            return lst[index - 1]
        else:
            return None

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
            return ''

        ms = int(ms)

        t = datetime(1970, 1, 1) + timedelta(milliseconds=ms)
        if returnTime:
            return t
        return t.strftime("%H:%M:%S")


    @classmethod
    def getTimezoneOffset(cls, settings):
        if settings['display']['use local timezone'] == 1:
            return timedelta(seconds=-(time.timezone if (time.localtime().tm_isdst == 0) else time.altzone))
        else:
            return timedelta(seconds=0)


    @classmethod
    def getMean(cls, data):
        mean1 = None
        if len(data) > 0:
            mean1 = mean(data)
        return mean1

    @classmethod
    def getStdev(cls, data):
        try:
            return stdev(data)
        except Exception as e:
            return None

    @classmethod
    def getQuotient(cls, dividend, divisor):
        quotient = None
        try:
            quotient = dividend/divisor
        except Exception as e:
            pass
        return quotient

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
    def formatValue(cls, value, isTime=False, isPercent=False):
        if value is None:
            return ""
        if type(value) == str:
            return value
        if type(value) == int:
            if isTime:
                valueDatetime = datetime(year=1970, month=1, day=1) + timedelta(seconds=value % 3600)
                return str(math.trunc(value/3600)) + valueDatetime.strftime('%M:%S')
            else:
                return str(value)
        if type(value) == float:
            if isTime:
                valueDatetime = datetime(year=1970, month=1, day=1) + timedelta(seconds=value % 3600)
                return str(math.trunc(value/3600)) + valueDatetime.strftime('%M:%S')
            else:
                if isPercent:
                    return str(round(value * 100, 1)) + '%'
                else:
                    return str(round(value, 1))
        if type(value) == timedelta:
            if isTime:
                valueDatetime = datetime(year=1970, month=1, day=1) + value
                return valueDatetime.strftime("%M:%S.") + str(round(int(10 * ((value / timedelta(seconds=1)) % 1)), 0))
            else:
                return value/timedelta(seconds=1)

    @classmethod
    def floatList(cls, list):
        for i in range(len(list)):
            list[i] = float(list[i])
        return list

    @classmethod
    def getRegressionLine(cls, x_list, y_list):
        # Convert x and y to numpy arrays
        x = np.array(x_list)
        y = np.array(y_list)

        # Calculate the slope and y-intercept of the regression line
        m, b = np.polyfit(x, y, 1)

        # Calculate the residuals
        residuals = y - (m * x + b)

        # Calculate the residual standard deviation (s)
        s = np.std(residuals, ddof=1)

        return m, b, s

    @classmethod
    def getResidual(cls, y, m, x, b):
        return y - m * x - b

    @classmethod
    def remove_top_X_percent(cls, data, x):
        # Determine the number of elements to remove
        num_to_remove = int(len(data) * x)

        # Sort the data in descending order
        sorted_data = sorted(data, reverse=False)

        # Remove the top 10% of values
        pruned_data = sorted_data
        if num_to_remove != 0:
            pruned_data = sorted_data[:-num_to_remove]
        return pruned_data

    @classmethod
    def findNormalDist(cls, data):
        data = sorted(data)
        for i in range(len(data), 0, -1):
            if mean(data) > median(data):
                data.pop(len(data) - 1)
            else:
                break
        return data

    @classmethod
    def getMode(cls, data, bin_size):
        # Calculate the number of bins needed to fit all the data
        bins = (len(data) + bin_size - 1) // bin_size

        # Create a list to store the count of data points in each bin
        bin_counts = [0] * bins

        # Loop through the data points and count how many are in each bin
        for i, point in enumerate(data):
            bin_index = i // bin_size
            bin_counts[bin_index] += 1

        # Find the bin with the most data points and return its index
        max_count = max(bin_counts)
        return bin_counts.index(max_count)

    @classmethod
    def get_percentile(cls, data, score):
        """
        Calculate the percentile rank of a score within a dataset.

        Parameters:
        - data (array-like): The dataset of scores.
        - score (float): The score to evaluate.

        Returns:
        - float: The percentile rank of the score within the dataset, as a percentage (0-100).
        """

        # Convert data to a sorted numpy array
        sorted_data = np.sort(data)

        # Find the index of the score in the sorted array
        index = np.searchsorted(sorted_data, score)

        # Calculate the percentile rank as a percentage
        percentile_rank = (index / len(sorted_data)) * 100

        return percentile_rank
