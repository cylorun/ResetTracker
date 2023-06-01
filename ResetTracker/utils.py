from statistics import mean, stdev, median
import scipy.stats as stats
import numpy as np
import datetime
from datetime import datetime, timedelta
import json
from datetime import time
import sys
import time
import math
import statsmodels.api as sm

multiCheckSupported = True

if sys.platform.startswith("win32"):
    from ctypes import create_unicode_buffer, windll

elif sys.platform.startswith("darwin"):
    print("Warning: On MacOS, do not put OBS in fullscreen mode.") # because of the checks used
    try:
        from AppKit import NSWorkspace
        from Quartz import (
            CGWindowListCopyWindowInfo,
            kCGWindowListOptionOnScreenOnly,
            kCGNullWindowID
        )
    except ModuleNotFoundError:
        multiCheckSupported = False
        print("If you are running multi on MacOS, you should run this command in your terminal: pip install pyobjc")

elif sys.platform.startswith("linux"):
    # xdotool is used to get the foreground window title, which requires x11
    import subprocess
    if subprocess.run(["echo", "$XDG_SESSION_TYPE"]).stdout != "x11":
        multiCheckSupported = False

else:
    multiCheckSupported = False
    print("can minecraft even run on your os lol")

if not multiCheckSupported:
    print("The tracker does not support multi for your software, so it will assume that you are running single instance.")

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
    def isOnWallScreen(cls):
        # if we can't check for multi, we assume that it isn't there
        if not multiCheckSupported:
            return False
        
        if sys.platform.startswith("win32"):
            hWnd = windll.user32.GetForegroundWindow()
            length = windll.user32.GetWindowTextLengthW(hWnd)
            buf = create_unicode_buffer(length + 1)
            windll.user32.GetWindowTextW(hWnd, buf, length + 1)
            return "Fullscreen Projector" in buf.value or "Full-screen Projector" in buf.value
        
        elif sys.platform.startswith("darwin"):
            curr_app = NSWorkspace.sharedWorkspace().frontmostApplication()
            curr_pid = NSWorkspace.sharedWorkspace().activeApplication()["NSApplicationProcessIdentifier"]
            curr_app_name = curr_app.localizedName()
            options = kCGWindowListOptionOnScreenOnly
            windowList = CGWindowListCopyWindowInfo(options, kCGNullWindowID)
            for window in windowList:
                pid = window["kCGWindowOwnerPID"]
                ownerName = window["kCGWindowOwnerName"]
                geometry = dict(window["kCGWindowBounds"])
                windowTitle = window.get("kCGWindowName", u"Unknown")
                # window name is rarely used on mac so we assume that if an obs window goes over the taskbar (aka fullscreen), it's a projector
                if curr_pid == pid and ownerName == "OBS Studio" and geometry["Y"] == 0:
                    return True
            return False
        
        elif sys.platform.startswith("linux"):
            process = subprocess.run(["xdotool", "getactivewindow", "getwindowname"], capture_output=True, text=True)
            title = process.stdout
            return "Fullscreen Projector" in title or "Full-screen Projector" in title

    @classmethod
    def ms_to_string(cls, ms, returnTime=False):
        if ms is None:
            return ''

        ms = int(ms)
        td = timedelta(milliseconds=ms)
        if returnTime:
            return datetime(1970, 1, 1) + td
        if not timedelta(hours=0) < td < timedelta(hours=12):
            td = timedelta(days=1) - td
        t = datetime(1970, 1, 1) + td
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
    def formatValue(cls, value, moe=None, dp=1, isNPH=False, isTime=False, isPercent=False, includeHours=False):
        if value is None:
            return ""
        if type(value) == str:
            return value
        if type(value) == int:
            if isTime:
                valueDatetime = datetime(year=1970, month=1, day=1) + timedelta(seconds=value % 3600)
                return str(math.trunc(value/3600)) + ':' + valueDatetime.strftime('%M:%S')
            else:
                return str(value)
        if type(value) == float:
            if isTime:
                valueDatetime = datetime(year=1970, month=1, day=1) + timedelta(seconds=value % 3600)
                if includeHours:
                    return str(math.trunc(value / 3600)) + ':' + valueDatetime.strftime('%M:%S') + '.' + str(round(int(10 * (value % 1)), 0))
                else:
                    if moe is not None:
                        return valueDatetime.strftime('%M:%S') + '.' + str(round(int(10 * (value % 1)), 0)) + " +- " + str(round(moe, dp))
                    else:
                        return valueDatetime.strftime('%M:%S') + '.' + str(round(int(10 * (value % 1)), 0))
            elif isPercent:
                if moe is not None:
                    return str(round(value * 100, dp)) + '% +- ' + str(round(moe, dp)) + '%'
                else:
                    return str(round(value * 100, dp)) + '%'
            elif isNPH:
                if moe is not None:
                    return str(round(value, dp)) + ' +- ' + str(round(moe, dp))
                else:
                    return str(round(value, dp))
            else:
                return str(round(value, dp))
        if type(value) == timedelta:
            print('x')
            if isTime:
                valueDatetime = datetime(year=1970, month=1, day=1) + value
                if includeHours:
                    return str(math.trunc((value / timedelta(seconds=1)) / 3600)) + ':' + valueDatetime.strftime("%M:%S") + '.' + str(round(int(10 * ((value / timedelta(seconds=1)) % 1)), 0))
                else:
                    return valueDatetime.strftime("%M:%S") + '.' + str(round(int(10 * ((value / timedelta(seconds=1)) % 1)), 0))
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

        # Calculate the slope, y-intercept, R-squared, and p-value
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

        # Calculate the residuals
        residuals = y - (slope * x + intercept)

        # Calculate the residual standard deviation (s)
        s = np.std(residuals, ddof=1)

        # Calculate the R-squared value
        r_squared = r_value ** 2

        return slope, intercept, s, r_squared, p_value

    @classmethod
    def getResidual(cls, y, m, x, b):
        return y - m * x - b

    @classmethod
    def t_int_moe(cls, sample_size, sample_std, confidence_level):
        print('t')
        # Calculate the critical value based on the confidence level and degrees of freedom
        degrees_of_freedom = sample_size - 1
        critical_value = stats.t.ppf((1 + confidence_level) / 2, degrees_of_freedom)

        # Calculate the margin of error
        margin_of_error = critical_value * (sample_std / (sample_size ** 0.5))
        print(margin_of_error)
        return margin_of_error

    @classmethod
    def z_int_moe(cls, sample_size, sample_num, confidence_level):
        print('z')
        sample_proportion = sample_num/sample_size

        # Calculate the critical value based on the confidence level
        critical_value = stats.norm.ppf((1 + confidence_level) / 2)

        # Calculate the margin of error
        margin_of_error = critical_value * ((sample_proportion * (1 - sample_proportion)) / sample_size) ** 0.5
        print(margin_of_error)
        return margin_of_error

    @classmethod
    def xph_int_moe1(cls, xph, n, confidence_level):
        critical_value = stats.poisson.ppf((1 + confidence_level) / 2, xph)
        print(critical_value)
        margin_of_error = critical_value * math.sqrt(xph / n)
        return margin_of_error

    @classmethod
    def xph_int_moe2(cls, xph, n, confidence_level):
        critical_value = stats.norm.ppf((1 + confidence_level) / 2)
        margin_of_error = critical_value * math.sqrt(xph / n)
        return margin_of_error

    @classmethod
    def slope_int_moe(cls, x, y, confidence_level, returnStandard=False):
        # Extract the variables from the data

        # Calculate the number of data points
        n = len(x)

        # Calculate the means of x and y
        x_mean = np.mean(x)
        y_mean = np.mean(y)

        # Calculate the sum of squared deviations
        ss_xx = np.sum((x - x_mean) ** 2)
        ss_yy = np.sum((y - y_mean) ** 2)
        ss_xy = np.sum((x - x_mean) * (y - y_mean))

        # Calculate the slope of the linear regression model
        slope = ss_xy / ss_xx

        # Calculate the residual sum of squares
        residuals = [y1 - (slope * x1) for x1, y1 in zip(x, y)]
        rss = np.sum([residual ** 2 for residual in residuals])

        # Calculate the degrees of freedom
        df = n - 2

        # Calculate the standard error of the slope
        standard_error = np.sqrt(rss / (df * ss_xx))

        # Calculate the critical value based on the t-distribution and confidence level
        critical_value = 1
        if not returnStandard:
            critical_value = stats.t.ppf((1 + confidence_level) / 2, df)

        # Calculate the margin of error
        margin_of_error = critical_value * standard_error

        # Return the t-interval for the slope as a tuple
        return slope, margin_of_error

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
