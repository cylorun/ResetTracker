import os
import shutil
from zipfile import ZipFile
import wget
import requests
import json
import time
import tkinter as tk
import threading


def unzip(path):
    with ZipFile(path) as zfile:
        zfile.extractall(path='temp/update')


def downloadSource():
    response1 = requests.get("https://api.github.com/repos/pncakespoon1/ResetTracker/releases/latest")
    releaseTag = response1.json()["name"]
    URL = "https://github.com/pncakespoon1/ResetTracker/archive/refs/tags/" + releaseTag + ".zip"
    os.makedirs("temp/update/", exist_ok=True)
    response2 = wget.download(URL, "temp/update/ResetTracker2.zip")


def updateSource():
    downloadSource()
    unzip('temp/update/ResetTracker2.zip')

    oldSettingsFile = open('/data/settings.json')
    oldSettings = json.load(oldSettingsFile)
    newSettingsFile = open('/temp/update/ResetTracker2/data/settings.json')
    newSettings = json.load(newSettingsFile)
    for key1 in oldSettings.keys():
        for key2 in oldSettings[key1].keys():
            newSettings[key1][key2] = oldSettings[key1][key2]
    oldSettingsFile.close()
    newSettingsFile.close()
    json.dump(newSettings, open('temp/update/ResetTracker2/data/settings.json', 'w'))

    oldConfigFile = open('data/config.json')
    oldConfig = json.load(oldConfigFile)
    newConfigFile = open('temp/update/ResetTracker2/data/config.json')
    newConfig = json.load(newConfigFile)
    for key in oldConfig.keys():
        if key != 'version':
            newConfig[key] = oldConfig[key]
    oldConfigFile.close()
    newConfigFile.close()
    json.dump(newConfig, open('temp/update/ResetTracker2/data/config.json', 'w'))

    shutil.rmtree('data')

    files = os.listdir(".")
    for file in files:
        if file != "databaseCredentials.json":
            os.remove(file)

    shutil.move('temp/update/ResetTracker2/data', '.')

    files = os.listdir("temp/update/ResetTracker2")
    for file in files:
        if "." in file:
            shutil.move('temp/update/ResetTracker2/' + file, '.')

    os.remove('temp/update/ResetTracker2.zip')
    shutil.rmtree('temp/update/ResetTracker2')


def downloadExe():
    response1 = requests.get("https://api.github.com/repos/pncakespoon1/ResetTracker/releases/latest")
    releaseTag = response1.json()["name"]
    URL = "https://github.com/pncakespoon1/ResetTracker/releases/download/" + releaseTag + "/ResetTracker2.zip"
    response2 = wget.download(URL, "temp/update/ResetTracker2.zip")


def updateExe():
    downloadExe()
    unzip('temp/update/ResetTracker2.zip')

    oldSettingsFile = open('data/settings.json')
    oldSettings = json.load(oldSettingsFile)
    newSettingsFile = open('temp/update/ResetTracker2/data/settings.json')
    newSettings = json.load(newSettingsFile)
    for key1 in oldSettings.keys():
        for key2 in oldSettings[key1].keys():
            newSettings[key1][key2] = oldSettings[key1][key2]
    oldSettingsFile.close()
    newSettingsFile.close()
    json.dump(newSettings, open('temp/update/ResetTracker2/data/settings.json', 'w'))

    oldConfigFile = open('data/config.json')
    oldConfig = json.load(oldConfigFile)
    newConfigFile = open('temp/update/ResetTracker2/data/config.json')
    newConfig = json.load(newConfigFile)
    for key in oldConfig.keys():
        if key != 'version':
            newConfig[key] = oldConfig[key]
    oldConfigFile.close()
    newConfigFile.close()
    json.dump(newConfig, open('temp/update/ResetTracker2/data/config.json', 'w'))

    shutil.rmtree('data')
    os.remove('gui.exe')

    relativeDir = os.path.abspath('temp')
    relativeDir = relativeDir[:len(relativeDir) - 5]
    shutil.move('temp/update/ResetTracker2/data', relativeDir)
    shutil.move('temp/update/ResetTracker2/ResetTracker2.exe', relativeDir)
    os.remove('temp/update/ResetTracker2.zip')
    shutil.rmtree('temp/update/ResetTracker2')


def update():
    if getattr(sys, 'frozen', False):  # if running in a PyInstaller bundle
        updateExe()
    else:
        updateSource()
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

