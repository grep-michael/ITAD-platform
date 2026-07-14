
import logging,subprocess,os,sys,pathlib,time
import xml.etree.ElementTree as ET
from Utilities.Config import ConfigLoader,Config
from Utilities.discord_noitification import *
ConfigLoader.init()
from Services.SegmentUploader import SegmentUploader
from Utilities.Marvell.executor import RemoveMarvellRaid
from Utilities.PCIChecker import *
from Utilities.Utils import CommandExecutor,DeviceScanner,PackageManager
from Utilities.Finisher import Finisher
from Utilities.LogFinder import LogFinder
from Razor.RazorClient import *
from Services.FTPManager import *
from Services.NetworkManager import NetworkManager
from Services.ShareManager import ShareManager
from Application import Application
from Services.Parsing.HardwareTreeBuilder import HardwareTreeBuilder
from PyQt5.QtWidgets import QApplication, QMessageBox
#TODO
#SM3E152CB2 <- pentium that isnt detected

print(Config.VERSION)
print("Debug: ",Config.DEBUG)
print("Upload to share: ",Config.UPLOAD_TO_SHARE)


if not os.path.exists("./logs/"):
    os.mkdir("./logs/")

logging.basicConfig(filename='./logs/ITAD_platform.log', level=logging.INFO,filemode="w")
logging.info(Config.VERSION)

RemoveMarvellRaid()

net_manager = NetworkManager()

net_manager.connect()
net_manager.refresh_ntpd()
try:
    PackageManager.install_packages()
except:
    pass
DeviceScanner.create_system_spec_files()
root:ET.Element = HardwareTreeBuilder.build_hardware_tree()



#if "confirm" in Config.process:
#    app = Application(root)
#    
#    pcichecker = PCIChecker()
#    if len(root.findall("Storage"))==0:
#        pcichecker.check_problem_devices()
#    
#    app.run()

Finisher.finialize_process(root)
serial = root.find(".//System_Serial_Number").text
errorMSG = ""
errorFields = []

client = RazorClient()
assets, err = client.Assets.Get().By_Serial(serial)
if err != None or len(assets) == 0:
    errorMSG += f"Failed to find Asset by serial number: {err}\n"
if len(assets) >= 1:
    asset = assets[0]
    root.find(".//Unique_Identifier").text = asset.uniqueId

storageCount = len(root.findall(".//Storage"))
if storageCount<2:
    errorMSG += f"Storage Count is incorrect\n"
    errorFields.append({"name":"Storage Count","value":f"{storageCount}"})

networkCount = len(root.findall(".//Slot_1"))
if networkCount < 1:
    errorMSG += f"No Network interfaces\n"


while not net_manager.can_ping_google():
    print("no internet displaying dialog")
    time.sleep(5)

if len(errorFields) > 0 or errorMSG != "":
    err = SegmentUploader().UploadXML(root)
    if err != None:
        errorMSG += f"{err}\n"
        errorFields.append({"name":"API Upload Error","value":err})

print("has internet running uploads")
lf = LogFinder()
uuid = lf.find_uuid()
share_manager = ShareManager()
share_manager.upload_dir("./logs",uuid)
share_manager.close_share()

print("Starting ftp upload...")
logging.info("Starting ftp upload...")
ftp = FTPUploadStrategy()
ret = ftp.upload_file("./logs/{}.xml".format(uuid))
if ret == False:
    errorMSG+= "Razor ftp Uploader failed\n"    
print("FTP upload return: {}".format(ret))
logging.info("FTP upload return: {}".format(ret))

if len(errorFields) > 0 or errorMSG != "":
    SendDiscordError(f"{serial} Errors",errorMSG,errorFields)
else:
    SendDiscordSuccess(f"{serial} Success","No errors detected")
