import os
import shutil
from zipfile import ZipFile
import wget
import requests
import json
import sys
import importlib

tracker = importlib.import_module("tracker")


def compare_versions(current_version, latest_version):
    print(current_version)
    print(latest_version)
    current_parts = [int(x) for x in current_version.split('.')]
    latest_parts = [int(x) for x in latest_version.split('.')]
    for i in range(3):
        if latest_parts[i] > current_parts[i]:
            return True
        elif latest_parts[i] < current_parts[i]:
            return False
    if current_version == latest_version:
        return False
    print("error in version parsing")
    raise Exception


def checkUpdateAvailable():
    response = requests.get("https://api.github.com/repos/pncakespoon1/ResetTracker/releases/latest")
    # Check if the request was successful
    if response.status_code == 200:
        # Get the JSON data from the response
        release_data = response.json()

        # Extract the tag name from the release data
        latest_tag = release_data["tag_name"]
    else:
        return False
    return compare_versions(tracker.__version__, latest_tag)


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
    items = os.listdir('temp/update')
    directories = [item for item in items if os.path.isdir(os.path.join('temp/update', item))]

    if os.path.exists('default'):
        os.remove('default')
    shutil.copytree('temp/update/' + directories[0] + '/ResetTracker/default', 'default')
    os.rename('temp/update/' + directories[0] + '/ResetTracker/default', 'temp/update/' + directories[0] + '/ResetTracker/data')

    oldSettingsFile = open('data/settings.json')
    oldSettings = json.load(oldSettingsFile)
    newSettingsFile = open('temp/update/' + directories[0] + '/ResetTracker/data/settings.json')
    newSettings = json.load(newSettingsFile)
    for key in oldSettings.keys():
        newSettings[key] = oldSettings[key]
    oldSettingsFile.close()
    newSettingsFile.close()
    json.dump(newSettings, open('temp/update/' + directories[0] + '/ResetTracker/data/settings.json', 'w'))

    shutil.rmtree('data')

    files = os.listdir(".")
    for file in files:
        if file not in ['temp', 'obs']:
            os.remove(file)

    shutil.move('temp/update/' + directories[0] + '/ResetTracker/data', '.')

    files = os.listdir('temp/update/' + directories[0] + '/ResetTracker')
    for file in files:
        if "." in file:
            shutil.move('temp/update/' + directories[0] + '/ResetTracker/' + file, '.')

    print(1)
    os.remove('temp/update/ResetTracker2.zip')
    print(2)
    shutil.rmtree('temp/update/' + directories[0] + '/ResetTracker')
    print(3)


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
    for key in oldSettings.keys():
        newSettings[key] = oldSettings[key]
    oldSettingsFile.close()
    newSettingsFile.close()
    json.dump(newSettings, open('temp/update/ResetTracker2/data/settings.json', 'w'))

    shutil.rmtree('data')
    os.remove('ResetTracker2.exe')

    relativeDir = os.path.abspath('temp')
    relativeDir = relativeDir[:len(relativeDir) - 5]
    shutil.move('temp/update/ResetTracker2/data', relativeDir)
    shutil.move('temp/update/ResetTracker2/ResetTracker2.exe', relativeDir)
    os.remove('temp/update/ResetTracker2.zip')
    shutil.rmtree('temp/update/ResetTracker2')


def update():
    if checkUpdateAvailable():
        if getattr(sys, 'frozen', False):  # if running in a PyInstaller bundle
            updateExe()
        else:
            updateSource()
    else:
        print("no update available")


if __name__ == "__main__":
    update()
