
import logging,subprocess,os,sys,pathlib
import xml.etree.ElementTree as ET
from Utilities.Config import ConfigLoader,Config
ConfigLoader.init()

from Utilities.PCIChecker import *
from Utilities.Utils import CommandExecutor,DeviceScanner,PackageManager
from Utilities.Finisher import Finisher
from Utilities.LogFinder import LogFinder
from Services.FTPManager import *
from Services.NetworkManager import NetworkManager
from Services.ShareManager import ShareManager
from Application import Application
from Services.Parsing.HardwareTreeBuilder import HardwareTreeBuilder
from PyQt5.QtWidgets import QApplication, QMessageBox
#TODO
#not smaller than 4 gigs
#network controller/view, ability to skip ntp updates and what not

print(Config.VERSION)
print("Debug: ",Config.DEBUG)
print("Upload to share: ",Config.UPLOAD_TO_SHARE)


if not os.path.exists("./logs/"):
    os.mkdir("./logs/")

logging.basicConfig(filename='./logs/ITAD_platform.log', level=logging.INFO,filemode="w")

logging.info(Config.VERSION)

if Config.DEBUG == "False" and "connect" in Config.process:
    net_manager = NetworkManager()
    net_manager.connect()
    net_manager.refresh_ntpd()

if Config.DEBUG == "False" and "dump" in Config.process:
    try:
        PackageManager.install_packages()
    except:
        pass
    DeviceScanner.create_system_spec_files()

if "dump" in Config.process:
    root:ET.Element = HardwareTreeBuilder.build_hardware_tree()



if "confirm" in Config.process:
    app = Application(root)
    
    pcichecker = PCIChecker()
    if len(root.findall("Storage"))==0:
        pcichecker.check_problem_devices()
    
    app.run()
    Finisher.finialize_process(root)


def show_confirm_dialog(title="Confirm Action", message="Are you sure?"):
    # Check if QApplication is already running
    app = QApplication.instance()
    should_exit = False
    if app is None:
        app = QApplication(sys.argv)
        should_exit = True

    # Create and configure the dialog
    msg_box = QMessageBox()
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.setIcon(QMessageBox.Question)
    msg_box.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ok)
    msg_box.setDefaultButton(QMessageBox.Ok)

    # Execute the dialog and get the result
    result = msg_box.exec_()
    confirmed = result == QMessageBox.Ok

    if should_exit:
        app.quit()

    return confirmed

if Config.UPLOAD_TO_SHARE == "True" and "upload" in Config.process:
    lf = LogFinder()
    uuid = lf.find_uuid()
    
    share_manager = ShareManager()
    share_manager.mount_share()
    share_manager.upload_dir("./logs",uuid)
    share_manager.close_share()

    upload = show_confirm_dialog(title="Upload to razor?",message="Upload to razor?")
    if upload:
        print("Starting ftp upload...")
        ftp = FTPUploadStrategy()
        ret = ftp.upload_file("./logs/{}.xml".format(uuid))
        print("FTP upload return: {}".format(ret))


