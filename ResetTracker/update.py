import os
import shutil
from zipfile import ZipFile
import wget
import requests
import json
import time
import stat
import tkinter as tk
import threading


def unzip(path):
    with ZipFile(path) as zfile:
        zfile.extractall(path='temp/update')


def download():
    response1 = requests.get("https://api.github.com/repos/pncakespoon1/ResetTracker/releases/latest")
    releaseTag = response1.json()["name"]
    URL = "https://github.com/pncakespoon1/ResetTracker/releases/download/" + releaseTag + "/ResetTracker2.0.zip"
    response2 = wget.download(URL, "temp/update/ResetTracker2.0.zip")


def update():
    download()
    unzip('temp/update/ResetTracker2.0.zip')

    oldSettingsFile = open('data/settings.json')
    oldSettings = json.load(oldSettingsFile)
    newSettingsFile = open('temp/update/ResetTracker2.0/data/settings.json')
    newSettings = json.load(newSettingsFile)
    for key1 in oldSettings.keys():
        for key2 in oldSettings[key1].keys():
            newSettings[key1][key2] = oldSettings[key1][key2]
    oldSettingsFile.close()
    newSettingsFile.close()
    json.dump(newSettings, open('temp/update/ResetTracker2.0/data/settings.json', 'w'))

    oldConfigFile = open('data/config.json')
    oldConfig = json.load(oldConfigFile)
    newConfigFile = open('temp/update/ResetTracker2.0/data/config.json')
    newConfig = json.load(newConfigFile)
    for key in oldConfig.keys():
        if key != 'version':
            newConfig[key] = oldConfig[key]
    oldConfigFile.close()
    newConfigFile.close()
    json.dump(newConfig, open('temp/update/ResetTracker2.0/data/config.json', 'w'))

    shutil.rmtree('data')
    os.remove('gui.exe')

    relativeDir = os.path.abspath('temp')
    relativeDir = relativeDir[:len(relativeDir) - 5]
    shutil.move('temp/update/ResetTracker2.0/data', relativeDir)
    shutil.move('temp/update/ResetTracker2.0/gui.exe', relativeDir)
    os.remove('temp/update/ResetTracker2.0.zip')
    shutil.rmtree('temp/update/ResetTracker2.0')
    root.destroy()


if __name__ == "__main__":
    time.sleep(3)
    root = tk.Tk()
    root.wm_geometry("250x100")
    label = tk.Label(root, text='Updating...')
    label.pack(side="top", fill="both", expand=True)
    t = threading.Thread(target=update, name="updateGithub")
    t.daemon = True
    t.start()
    root.mainloop()

