from PyQt5.QtWidgets import *
from GUIs.WidgetProxies import *
from GUIs.CustomWidgets import *
from GUIs.CustomWidgets.Overview import *
#from GUIs.CustomWidgets.ErasureWindow import *
from Erasure.app import *
import xml.etree.ElementTree as ET

#CLASS_ASSOCIATION = {
#    "System_Information/Unique_Identifier":ElementNode,
#    "System_Information/Tech_ID":TechIDList,
#    "System_Information/System_Category":SystemCategory,
#    "Devices/Webcam":WebCam,
#    "Devices/Graphics_Controller":ElementNode,
#    "Devices/Optical_Drive":ElementNode,
#    "Devices/CPU":ElementNode,
#    "Devices/Memory":ElementNode,
#    "Devices/Display":ElementNode,
#    "Devices/Battery":ElementNode,
#    "Devices/Storage":ElementNode,
#    "System_Information/System_Notes":NotesWidget,
#    "System_Information/Cosmetic_Grade":GradeList,
#    "System_Information/LCD_Grade":GradeList,
#    "System_Information/Final_Grade":FinalGrade,
#}
PROXY_ASSOCIATION = {
    "System_Information/Unique_Identifier":UUIDProxy,
    "System_Information/Tech_ID":TechIDProxy,
    "System_Information/System_Category":CategoryProxy,
    "Devices/Webcam":WebcamProxy,
    "Devices/Graphics_Controller":GraphicsControllerProxy,
    "Devices/Optical_Drive":OpticalDriveProxy,
    "Devices/CPU":CPUProxy,
    "Devices/Memory":MemoryProxy,
    "Devices/Display":DisplayProxy,
    "Devices/Battery":BatteryProxy,
    "Devices/Storage":StorageProxy,
    "System_Information/System_Notes":SystemNotesProxy,
    "System_Information/Cosmetic_Grade":CosmeticGradeProxy,
    "System_Information/LCD_Grade":LCDGradeProxy,
    "System_Information/Final_Grade":FinalGradeProxy,
}


class WidgetBuilder():
    def __init__(self,tree:ET.Element):
        self.tree = tree
        self.root_path = ".//SYSTEM_INVENTORY/"

    def show_single_widget(self,parent):
        """
        used only for testing
        """
        list = []
        key = "Devices/Storage"
        proxy = StorageProxy

        nodes = self.tree.findall(self.root_path+key)
        #for node in nodes:
        #    list.append(proxy.get_host(parent,self.tree,node))
        #list.append(Overview(self.tree))
        #list.append(EasureWindow(self.tree))
        list.append(ErasureApp(self.tree))
        list.append(ExitWindow())
        return list

    def build_widget_list(self,parent):
        return self.show_single_widget(parent)
        widget_list = []
        for key,proxy in PROXY_ASSOCIATION.items():
            nodes = self.tree.findall(self.root_path+key)
            for node in nodes:
                widget_list.append(proxy.get_host(parent,self.tree,node))

        widget_list.append(Overview(self.tree))
        widget_list.append(ErasureApp(self.tree))
        widget_list.append(ExitWindow())
        return widget_list



    



