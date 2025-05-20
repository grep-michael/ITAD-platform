
import logging,subprocess,os,sys
import xml.etree.ElementTree as ET
from Utilities.Utils import CommandExecutor,DeviceScanner,PackageManager
from Utilities.Config import ConfigLoader,Config
ConfigLoader.init()

from Services.FTPManager import *
from Services.NetworkManager import NetworkManager
from Services.ShareManager import ShareManager
from Application import Application
from Services.Parsing.HardwareTreeBuilder import HardwareTreeBuilder
from Services.DataRefiner import *

#TODO
#not smaller than 4 gigs
#network controller/view, ability to skip ntp updates and what not

print(Config.VERSION)
print("Debug: ",Config.DEBUG)

print("Upload to share: ",Config.UPLOAD_TO_SHARE)

if not os.path.exists("./logs/"):
    os.mkdir("./logs/")

logging.basicConfig(filename='./logs/ITAD_platform.log', level=logging.INFO,filemode="w")

if Config.DEBUG == "False":
    net_manager = NetworkManager()
    net_manager.connect()
    net_manager.refresh_ntpd()

if Config.DEBUG == "False":
    PackageManager.install_packages()
    DeviceScanner.create_system_spec_files()

root = HardwareTreeBuilder.build_hardware_tree()
app = Application(root)
app.run()


LogRefiner.Refine_data()
XMLTreeRefiner.Refine_tree(root)

uuid = root.find(".//System_Information/Unique_Identifier").text

if Config.UPLOAD_TO_SHARE == "True":
    share_manager = ShareManager()
    share_manager.mount_share()
    share_manager.upload_dir("./logs",uuid)
    share_manager.close_share()

    import tkinter as tk
    from tkinter import messagebox
    root = tk.Tk()
    root.withdraw() 
    user_input = messagebox.askyesno("Confirmation","Upload to Razor")
    root.destroy()
    if user_input:
        ftp = FTPUploadStrategy()
        ftp.upload_file("./logs/{}.xml".format(uuid))