
import logging,subprocess,os
import xml.etree.ElementTree as ET
from Utilities.Utils import CommandExecutor,DeviceScanner,PackageManager,load_env_file
load_env_file()

from FTPManager import *
from NetworkManager import NetworkManager
from ShareManager import ShareManager
from GUIs.Application import *
from Parsing.HardwareTreeBuilder import HardwareTreeBuilder
from DataRefiner import *

#TODO
#erasure completed notification
#more logging
#TODO Application.py change setfocus to find child with object name and set focus to that child instead of using classes
#erasurewindow width is still messed up, cuts off first row on test pc4

print(os.environ["VERSION"])

DEBUG = True
COPY_FROM_SHARE = False
UPLOAD_TO_SHARE = False

logging.basicConfig(filename='ITAD_platform.log', level=logging.INFO,filemode="w")

net_manager = NetworkManager()
#net_manager.connect()

if not DEBUG:
    PackageManager.install_packages()
    DeviceScanner.create_system_spec_files()

if COPY_FROM_SHARE:
    #copy spec files from share
    machine_id = "Precision_Tower_3620"
    copy_cmd = "cp -r /mnt/network_drive/ITAD_platform/test_specs/{}/* ./specs/".format(machine_id)
    print("Copying spec from {}".format(machine_id))
    CommandExecutor.run(["mkdir ./specs/"],shell=True)
    CommandExecutor.run([copy_cmd],stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)

root = HardwareTreeBuilder.build_hardware_tree()

app = Application(root)
app.run()

#upload spec files to share
if UPLOAD_TO_SHARE:
    system_name = root.find(".//SYSTEM_INVENTORY/System_Information/System_Model").text.replace(" ","_")
    mkdir_cmd = "mkdir /mnt/network_drive/ITAD_platform/test_specs/{}".format(system_name)
    copy_cmd = "cp -r ./specs/* /mnt/network_drive/ITAD_platform/test_specs/{}".format(system_name)
    print("Saving specs to {}".format(system_name))
    CommandExecutor.run(["mount -t cifs  -o username=guest,password= //10.1.4.128/share /mnt/network_drive"],shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    CommandExecutor.run([mkdir_cmd],shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    CommandExecutor.run([copy_cmd],shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)

LogRefiner.Refine_data()
XMLTreeRefiner.Refine_tree(root)

uuid = root.find(".//System_Information/Unique_Identifier").text

if UPLOAD_TO_SHARE:
    share_manager = ShareManager()
    share_manager.mount_share()
    share_manager.upload_dir("./logs",uuid)
    share_manager.close_share()

    ftp = FTPUploadStrategy()
    ftp.upload_file("./logs/{}.xml".format(uuid))