__version__ = "2.0.12"

import sys
from constants import *
if not getattr(sys, 'frozen', False):  # if not running in a PyInstaller bundle
    try:
        from statistics import mean, stdev
        import datetime
        from datetime import datetime, timedelta
        import json
        from datetime import time
        import time
        import math
        import pygsheets
        import glob
        import os
        from watchdog.events import FileSystemEventHandler
        from watchdog.observers import Observer
        import requests
        import csv
        import webbrowser
        import re
        import tempfile
        import shutil
        import filecmp
        from nbtlib import nbt
        import wmi, win32process, win32gui, pythoncom
    except Exception as e:
        print(e)
        print("Run the following command in your terminal: pip install -r requirements.txt")
        sys.exit()
else:
    from statistics import mean, stdev
    import datetime
    from datetime import datetime, timedelta
    import json
    from datetime import time
    import time
    import math
    import pygsheets
    import glob
    import webbrowser
    import os
    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer
    import requests
    import csv
    import re
    import tempfile
    import shutil
    import filecmp
    from nbtlib import nbt
    import wmi, win32process, win32gui, pythoncom



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

"""
    STARTUP:
    Recreate data folder if not exists, copying it from the default folder
"""
if not os.path.exists("data"):
    os.makedirs("data")

for file in os.listdir("default"):
    if not os.path.exists(os.path.join("data", file)):
        shutil.copyfile(os.path.join("default", file), os.path.join("data", file))


"""
global variables
"""


if os.path.exists('stats.csv'):
    shutil.move('stats.csv', 'data/stats.csv')
if os.path.exists('temp.csv'):
    shutil.move('temp.csv', 'data/temp.csv')

SETTINGS_JSON = json.load(open(os.path.join(os.getcwd(),'data','settings.json'), "r"))
try:
    with open(os.path.join(os.getcwd(),'data','stats.csv'), 'x') as f:
        pass
except Exception as e:
    pass
wks1 = None
if getattr(sys, 'frozen', False):  # if running in a PyInstaller bundle
    base_path = sys._MEIPASS
else:
    base_path = os.path.abspath(".")
second = timedelta(seconds=1)
currentSessionMarker = 'X'




"""
global variables
"""


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


class Logistics:
    @classmethod
    def verify_settings(cls):

        global wks1
        try:
            gc_sheets = pygsheets.authorize(service_file="credentials.json")
            sh = gc_sheets.open_by_url(SETTINGS_JSON['sheet link'])
            wks1 = sh.worksheet_by_title('Raw Data')
        except FileNotFoundError:
            input("Put credentials.json in the same directory as the executable. Press enter when you have done this.")
            Logistics.verify_settings()
            return
        except pygsheets.AuthenticationError:
            input("Credentials.json is not valid. Press enter when you have fixed this.")
            Logistics.verify_settings()
            return
        except (pygsheets.SpreadsheetNotFound, pygsheets.NoValidUrlKeyFound):
            if SETTINGS_JSON["sheet link"] == "":
                SETTINGS_JSON["sheet link"] = input("Paste the link to your spreadsheet: ")
                Logistics.verify_settings()
                return
            else:
                try:
                    response = requests.get(SETTINGS_JSON["sheet link"])
                    if response.status_code != 200:
                        raise Exception
                except Exception:
                    print("Invalid link")
                    SETTINGS_JSON["sheet link"] = input("Paste the link to your spreadsheet: ")
                    Logistics.verify_settings()
                    return
        except pygsheets.WorksheetNotFound:
            input("The spreadsheet must have a subsheet named 'Raw Data'. Press enter when you have fixed this.")
            Logistics.verify_settings()
            return
        try:
            if not os.path.exists(SETTINGS_JSON["records path"]):
                raise Exception
        except Exception:
            SETTINGS_JSON["records path"] = input("Records path is nonexistent. Please enter your records path here: ").replace("\\", "/")
            Logistics.verify_settings()
            return

        with open("data/settings.json", "w") as settings_file:
            json.dump(SETTINGS_JSON, settings_file)

    

    @classmethod
    def find_save(cls, directory, record_path, save_name):
        # start_time = time.time()

        # for dir in os.listdir(os.path.join(directory, "instances")):
        #     try:
        #         save_path = os.path.join(directory, "instances", dir, ".minecraft/saves", save_name)
        #         if not os.path.exists(os.path.join(save_path, "speedrunigt/record.json")):
        #             raise Exception
        #     except:
        #         pass
        #     else:
        #         if filecmp.cmp(os.path.join(save_path, "speedrunigt/record.json"), record_path):
        #             return save_path

        # elapsed_time = time.time() - start_time
        # print("Save file not found.")
        # print("Elapsed time:", elapsed_time, "seconds")
        # return None
        home_dir = os.path.expanduser("~")
        with open(os.path.join(home_dir, 'speedrunigt', 'latest_world.json')) as f:
            j = json.load(f)


        return j['world_path']

    @classmethod
    def isOnWallScreen(cls):
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
        return t.strftime("%H:%M:%S")

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
            quotient = dividend / divisor
        except Exception as e:
            pass
        return quotient

    @classmethod
    def stringToDatetime(cls, DTString):
        components = DTString.split(" ")
        links = components[0].split("/") + components[1].split(":")
        return datetime(month=int(links[0]), day=int(links[1]), year=int(links[2]), hour=int(links[3]),
                        minute=int(links[4]), second=int(links[5]))

    @classmethod
    def stringToTimedelta(cls, TDString):
        parts = TDString.split(".")
        links = parts[0].split(":") 
        return timedelta(hours=int(links[0]), minutes=int(links[1]), seconds=int(links[2]))

class Sheets:

    @classmethod
    def setup(cls):
        wks1.update_row(index=1, values=HEADER_LABELS, col_offset=0)

    @classmethod
    def push_data(cls):
        with open("data/temp.csv", newline="") as f:
            reader = csv.reader(f)
            data = list(reader)
            f.close()
        try:
            if len(data) == 0:
                return
            wks1.insert_rows(values=data, row=3, number=1, inherit=False)
            f = open("data/temp.csv", "w+")
            f.close()

        except Exception as e2:
            print(23)
            print(e2)



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
        self.isFirstRun = '$' + __version__

    def ensure_run(self):
        if self.path is None:
            return False, "Path error"
        if self.data is None:
            return False, "Empty data error"
        return True, ""

    def on_created(self, evt, dt1=None):
        self.run = []
        self.path = evt.src_path
        with open(self.path, "r") as record_file:
            try:
                self.data = json.load(record_file)
            except Exception as e:
                print('Failed to load record file, trying again\n',e)
                time.sleep(1)
                self.on_created(evt)
                return
        
        if self.data is None:
            return

        validation = self.ensure_run()
        if not validation[0]:
            return
        has_done_something = False
        
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

        run_date = Logistics.ms_to_string(int(self.data["date"]), returnTime=True)
        has_done_something = False

        if "minecraft:story/smelt_iron" in adv: # has to obtain iron in order for the run to be tracked
            has_done_something = True

        if not has_done_something:
            return

        # Generate other stuff
        enter_type, gold_source, spawn_biome, iron_source, gold_dropped, trades, mobs_killed, food_eaten, travel_list = Tracking.getMiscData(stats, adv)
        try:
            pythoncom.CoInitialize()
            dat_path = os.path.join(Logistics.find_save(SETTINGS_JSON['mmc_path'], self.path, self.data['world_name']),'level.dat')
            nbtfile = nbt.load(dat_path)
            seed = nbtfile["Data"]["WorldGenSettings"]["seed"]
            seed = re.sub(r'[^0-9-]', '', str(seed))
        except Exception as e:
            print(e)
            seed = "Failed to get the seed"
        pythoncom.CoUninitialize()

        self.run.append(run_date)
        self.run.append(iron_source)
        self.run.append(enter_type)
        self.run.append(gold_source)
        self.run.append(spawn_biome)
        self.run.append(Logistics.ms_to_string(self.data['final_rta']))

        try:
            t = Logistics.ms_to_string(adv["minecraft:recipes/misc/charcoal"]['criteria']['has_log']['igt'])
            self.run.append(t)
        except KeyError as e:
            self.run.append('')

        try:
            t = Logistics.ms_to_string(adv["minecraft:story/iron_tools"]['criteria']['iron_pickaxe']['igt'])
            self.run.append(t)
        except KeyError as e:
            self.run.append('')

        for t in TIMELINES:
            if t in [i['name'] for i in self.data['timelines']]:
                idx = 0
                for i, o in enumerate(self.data['timelines']):
                    if o['name'] == t:
                        idx = i
                self.run.append(Logistics.ms_to_string(self.data['timelines'][idx]['igt']))
                continue
            self.run.append('')

        self.run.append(Logistics.ms_to_string(self.data['final_igt']))
        self.run.append(gold_dropped) 
        for sub, stat in STAT_CHECKS:
            try:
                self.run.append(stats[sub][stat])
                # print(f'{stat} : {stats[sub][stat]}')
            except KeyError:
                self.run.append('0')
                pass
        print(self.path)
        str_run = list(map(str, self.run))

        data1 = (str_run + trades + mobs_killed + food_eaten + travel_list + [seed])
        data2 = []
        for item in data1:
            if type(item) == str and ":" in item and item.count("-") < 2:
                data2.append(item)
            else:
                data2.append(item)

        self.isFirstRun = ''

        with open("data/stats.csv", "a", newline="") as outfile:
            writer = csv.writer(outfile)
            writer.writerow(data1)
        
        with open("data/temp.csv", "r") as infile:
            reader = list(csv.reader(infile))
            reader.insert(0, data2)
        with open("data/temp.csv", "w", newline="") as outfile:
            writer = csv.writer(outfile)
            for line in reader:
                writer.writerow(line)

        # updates displayed stats


        # Reset all counters/sums
        self.wall_resets = 0
        self.rta_spent = 0
        self.splitless_count = 0
        self.wall_time = 0
        self.break_time = 0
        self.rtaString = ''
        print("run tracked")



# tracking
class Tracking:
    
    @classmethod
    def startResetTracker(cls):
        Logistics.verify_settings()
        Tracking.trackResets()

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

        gold_dropped, gold_picked_up = "0", "0"
        trades_list = [0]*len(TRACKED_BARTERS)
        if "minecraft:picked_up" in stats:
            if 'minecraft:gold_ingot' in stats['minecraft:picked_up']:
                gold_picked_up = str(stats['minecraft:picked_up']['minecraft:gold_ingot'])

            for i in range(len(TRACKED_BARTERS)):
                if TRACKED_BARTERS[i] in stats["minecraft:picked_up"]:
                    trades_list[i] = int(stats["minecraft:picked_up"][TRACKED_BARTERS[i]])


        if 'minecraft:dropped' in stats:
            for k, v in stats['minecraft:dropped'].items():
                if k == 'minecraft:gold_ingot':
                    gold_dropped = str(v)
        
        gold_dropped =  int(gold_dropped) - int(gold_picked_up) # accounts for picking up gold when bartering
        
        blocks_mined_list = ['0'] * len(TRACKED_BLOCKS)

        if "minecraft:mined" in stats:
            for i in range(len(TRACKED_BLOCKS)):
                if TRACKED_BLOCKS[i] in stats["minecraft:mined"]:
                    blocks_mined_list[i] = str(stats["minecraft:mined"][TRACKED_BLOCKS[i]])



        killed_list = ['0']*len(TRACKED_MOBS)
        if 'minecraft:killed' in stats:
            for i in range(len(TRACKED_MOBS)):
                if TRACKED_MOBS[i] in stats["minecraft:killed"]:
                    killed_list[i] = str(stats["minecraft:killed"][TRACKED_MOBS[i]])
        
        food_list = ['0']*len(TRACKED_FOODS)
        if 'minecraft:used' in stats:
            for i in range(len(TRACKED_FOODS)):
                food_list[i] = str(stats['minecraft:used'].get(TRACKED_FOODS[i],0))

        dist_list = ['0']*len(TRAVEL_METHODS)
        for i, c in enumerate(TRAVEL_METHODS):
            try:
                dist_list[i] = str(stats['minecraft:custom'][c]/100)
            except KeyError:
                pass

        trades_list=  list(map(str, trades_list))
        return enter_type, gold_source, spawn_biome, iron_source, gold_dropped, trades_list, killed_list, food_list, dist_list


    @classmethod
    def trackResets(cls):
        if SETTINGS_JSON['generate-labels']:
            Sheets.setup()

        if not os.path.exists('data/temp.csv'):
            with open('data/temp.csv', 'w') as f:
                f.write('')

        while True:
            try:
                newRecordObserver = Observer()
                event_handler = NewRecord()
                newRecordObserver.schedule(
                    event_handler, SETTINGS_JSON["records path"], recursive=False)
                newRecordObserver.start()
            except Exception as e:
                print("Records directory could not be found")
            else:
                break
            

        live = True

        print("tracking")

        try:
            while live:
                Sheets.push_data()
                time.sleep(3)
        except Exception as e:
            print(26)
            print(e)
        finally:
            newRecordObserver.stop()
            newRecordObserver.join()


if __name__ == "__main__":
    Tracking.startResetTracker()

