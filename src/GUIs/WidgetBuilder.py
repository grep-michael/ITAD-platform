from PyQt5.QtWidgets import *
from GUIs.CustomWidgets import *
from GUIs.BaseWidgets import *


from collections import defaultdict


CLASS_ASSOCIATION = {
    "Unique_Identifier":ElementNode,
    "Tech_ID":TechIDList,
    "System_Category":SystemCategory,
    "Webcam":WebCam,
    "Graphics_Controller":ElementNode,
    "Optical_Drive":ElementNode,
    "CPU":ElementNode,
    "Memory":ElementNode,
    "Display":ElementNode,
    "Battery":ElementNode,
    "Storage_Data_Collection":ElementNode,
    "Storage":ElementNode,
    "System_Notes":NotesWidget,
    "Cosmetic_Grade":GradeList,
    "LCD_Grade":GradeList,
    "Final_Grade":FinalGrade,
}

class WidgetBuilder():
    def __init__(self,tree):
        self.tree = tree
        self.sys_info = self.tree.find(".//SYSTEM_INVENTORY/System_Information")
        self.devices = self.tree.find(".//SYSTEM_INVENTORY/Devices")

    def serve_devices(self,parent) -> defaultdict[str,list[QWidget]]:
        device_list = defaultdict(list)
        for device in self.devices:
            #print(device.tag,CLASS_ASSOCIATION[device.tag])
            device_list[device.tag].append( CLASS_ASSOCIATION[device.tag](device,parent))
        return device_list

    def serve_sys_info(self,parent) -> dict[str, 'ElementNode']:
        info_list = defaultdict(list)
        for info in self.sys_info:
            if info.tag in CLASS_ASSOCIATION:
                info_list[info.tag].append(CLASS_ASSOCIATION[info.tag](info,parent))
        return info_list
    

    



