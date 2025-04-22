
import logging,subprocess,os,sys
import xml.etree.ElementTree as ET
from Utilities.Utils import CommandExecutor,DeviceScanner,PackageManager,load_env_file

load_env_file()


from Services.FTPManager import *
from Services.NetworkManager import NetworkManager
from Services.ShareManager import ShareManager
from Application import *
from Services.Parsing.HardwareTreeBuilder import HardwareTreeBuilder
from Services.DataRefiner import *

#TODO
#erasure completed notification
#overview hight is fucked

#what do when no drive
#camera retake button
#sig check on an already wiped drive might cause problems for erasure processes that zero a disk, e.i before and after will be different
#cpu count, simply add the Count as a tag to all the CPU elements
#grabbing server raid controllers


print(os.environ["VERSION"])
print("Debug: ",os.environ["DEBUG"])
COPY_FROM_SHARE = False
UPLOAD_TO_SHARE = True

if not os.path.exists("./logs/"):
    os.mkdir("./logs/")
logging.basicConfig(filename='./logs/ITAD_platform.log', level=logging.INFO,filemode="w")

net_manager = NetworkManager()

if not os.environ["DEBUG"] == "True":
    net_manager.connect()
    net_manager.refresh_ntpd()

if not os.environ["DEBUG"] == "True":
    PackageManager.install_packages()
    DeviceScanner.create_system_spec_files()

if COPY_FROM_SHARE:
    #copy spec files from share
    machine_id = "OptiPlex_AIO_7410_65W"
    copy_cmd = "cp -r /mnt/network_drive/ITAD_platform/test_specs/{}/* ./specs/".format(machine_id)
    print("Copying spec from {}".format(machine_id))
    CommandExecutor.run(["mkdir ./specs/"],shell=True)
    CommandExecutor.run([copy_cmd],stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)

root = HardwareTreeBuilder.build_hardware_tree()

app = Application(root)
app.run()

#upload spec files to test share
if UPLOAD_TO_SHARE and os.environ["DEBUG"] == "True":
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

if UPLOAD_TO_SHARE:
    import tkinter as tk
    from tkinter import messagebox
    root = tk.Tk()
    root.withdraw() 
    user_input = messagebox.askyesno("Confirmation","Upload to Razor")
    root.destroy()
    if user_input:
        ftp = FTPUploadStrategy()
        ftp.upload_file("./logs/{}.xml".format(uuid))