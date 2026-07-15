
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
from Erasure.Services.WiperServices import WipeService
from Erasure.Controllers.DriveModel import DriveModel
#TODO
# this is fucking ugly and i hate the way it looks

print(Config.VERSION)
print("Debug: ",Config.DEBUG)
print("Upload to share: ",Config.UPLOAD_TO_SHARE)

def wipe_all_drives(xml:ET.Element):
    storages = xml.findall(".//Storage")
    for storage in storages:
        model = DriveModel(storage)
        if not model.removeable:
            print(f"Wiping drive {model.path}")
            try:
                service = WipeService(model,None)
                service.start_wipe()
                service._thread.wait(60000) #1 minute timeout

            #service.run_method_deterministic()
            except Exception as e:
                print("Error running erasure")
        else:
            print(f"{model.name} is removable, skipping...")
    
        

if not os.path.exists("./logs/"):
    os.mkdir("./logs/")

logging.basicConfig(filename='./logs/ITAD_platform.log', level=logging.INFO,filemode="w")
logging.info(Config.VERSION)
errorMSG = ""
errorFields = []


RemoveMarvellRaid()

net_manager = NetworkManager()
net_manager.connect()
net_manager.refresh_ntpd()

DeviceScanner.create_system_spec_files()
root:ET.Element = HardwareTreeBuilder.build_hardware_tree()
serial = root.find(".//System_Serial_Number").text

client = RazorClient()
err = client.Login()
if err != None:
    SendDiscordError(f"{serial}", f"error logging into razor: {err}")
    os._exit(1)

assets, err = client.Assets.Get().By_Serial(serial)
thisAsset = None
if err != None or len(assets) == 0:
    errorMSG += f"Failed to find Asset by serial number: {err}\n"
    SendDiscordError(f"{serial}", f"Failed to find Asset by serial number: {err}")
    os._exit(1)
if len(assets) >= 1:
    thisAsset = assets[0]
    root.find(".//Unique_Identifier").text = thisAsset.uniqueId

wipe_all_drives(root)
Finisher.finialize_process(root,client,thisAsset.customer)


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

if len(errorFields) <= 0 or errorMSG == "":
    err = SegmentUploader().UploadXML(root)
    if err != None:
        errorMSG += f"{err}\n"
        errorFields.append({"name":"API Upload Error","value":err})

print("has internet running uploads")
lf = LogFinder()
uuid = lf.find_uuid()
print(f"Found xml log to upload: {uuid}")

share_manager = ShareManager()

while not share_manager.mount_share():
    logging.info("Cant connect to share","Failed to connect to share, check internet")
    print("Cant connect to share","Failed to connect to share, check internet")
    time.sleep(5)

ret = share_manager.upload_dir("./logs",uuid)
if ret == False:
    errorMSG+= "Share Upload Failed\n"    
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



