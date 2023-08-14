import sys


if not getattr(sys, 'frozen', False):  # if not running in a PyInstaller bundle
    try:
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
        import pygsheets
        import glob
        import os
        from watchdog.events import FileSystemEventHandler
        from watchdog.observers import Observer
        import requests
        import webbrowser
        import csv
        import threading
        from functools import partial
        import io
        import re
        import tempfile
        import shutil
        import filecmp
        from nbtlib import nbt
    except Exception as e:
        print("Run the following command in your terminal: pip install -r requirements.txt")
        sys.exit()
else:
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
    import pygsheets
    import glob
    import os
    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer
    import requests
    import webbrowser
    import csv
    import threading
    from functools import partial
    import io
    import re
    import tempfile
    import shutil
    import filecmp
    from nbtlib import nbt


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
    import os
    session_type = os.environ.get('XDG_SESSION_TYPE')
    if session_type!="x11":
        multiCheckSupported = False

else:
    multiCheckSupported = False
    print("can minecraft even run on your os lol")

if not multiCheckSupported:
    print("The tracker does not support multi for your software, so it will assume that you are running single instance.")

headerLabels = ['Date and Time', 'Iron Source', 'Enter Type', 'Gold Source', 'Spawn Biome', 'RTA', 'Wood',
                'Iron Pickaxe', 'Nether', 'Bastion', 'Fortress', 'Nether Exit', 'Stronghold', 'End', 'Retimed IGT',
                'IGT', 'Gold Dropped', 'Blaze Rods', 'Blazes', '', '', '', '', '', '', 'Iron', 'Wall Resets Since Prev',
                'Played Since Prev', 'RTA Since Prev', 'Break RTA Since Prev', 'Wall Time Since Prev', 'Session Marker',
                'RTA Distribution', 'seed', 'Diamond Pick', 'Pearls Thrown', 'Deaths',
                'Obsidian Placed', 'Diamond Sword', 'Blocks Mined']


class Stats:
    @classmethod
    def fixCSV(cls):
        file_path = 'data/stats.csv'
        temp_file_path = tempfile.NamedTemporaryFile(mode='w', delete=False).name
        with open(file_path, 'r') as file, open(temp_file_path, 'w', newline='') as temp_file:
            reader = csv.reader(file)
            writer = csv.writer(temp_file)
            flag = False
            for row in reader:
                output_row = []
                if not flag:
                    for value in row:
                        if re.match(r'^\d{2}:\d{2}:\d{2}$', value):
                            value += '.000000'
                        elif re.match(r'^\d{2}:\d{2}:\d{2}\.\d{6}$', value):
                            flag = True
                        output_row.append(value)
                else:
                    output_row = row
                if len(output_row) == 34:
                    output_row = output_row[:19] + [""] * 6 + output_row[25:] + output_row[19:25]
                writer.writerow(output_row)

        # Replace the original file with the modified one
        shutil.move(temp_file_path, file_path)

    @classmethod
    def fixSheet(cls, wks):
        try:
            length = wks.cols
            extra_cols = []
            if length == 33:
                extra_cols.append(['seed'] + [""] * (wks.rows - 1))
            if 33 <= length <= 34:
                for i in range(20, 26):
                    extra_cols.append(wks.get_col(i))
                    wks.update_col(i, [""] * wks.rows)
            for i in range(length, length + len(extra_cols)):
                wks.insert_cols(col=i, number=1, values=[extra_cols[i - length]], inherit=True)
        except Exception as e:
            print(e)
            return

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


class Logistics:
    @classmethod
    def find_save(cls, directory, record_path, save_name):
        start_time = time.time()

        for dir in os.listdir(os.path.join(directory, "instances")):
            try:
                save_path = os.path.join(directory, "instances", dir, ".minecraft/saves", save_name)
                if not os.path.exists(os.path.join(save_path, "speedrunigt/record.json")):
                    raise Exception
            except:
                pass
            else:
                if filecmp.cmp(os.path.join(save_path, "speedrunigt/record.json"), record_path):
                    return save_path
        elapsed_time = time.time() - start_time
        print("Save file not found.")
        print("Elapsed time:", elapsed_time, "seconds")
        return None

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
            import subprocess
            process = subprocess.run(["xdotool", "getactivewindow", "getwindowname"], capture_output=True, text=True)
            title = process.stdout
            return "Projector" in title

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
        return t.strftime("%H:%M:%S.%f")


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
        parts = TDString.split(".")
        links = parts[0].split(":") + [parts[1]]
        return timedelta(hours=int(links[0]), minutes=int(links[1]), seconds=int(links[2]), microseconds=int(links[3]))

