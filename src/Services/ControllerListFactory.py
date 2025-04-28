from PyQt5.QtWidgets import *
from AttributeGathering.Controllers import *
from Erasure.ErasureController import *
from AttributeGathering.Views.ExitWindowView import ExitWindow
import xml.etree.ElementTree as ET
from Services.ControllerFactory import ControllerFactory

class ControllerListFactory():
    """
    Return a list of Controllers for the application to loop over
    """

    SYSTEM_SPEC_GATHERING_LIST = [
        #"System_Information/Unique_Identifier",
        #"System_Information/Tech_ID",
        #"System_Information/System_Category",
        #"Devices/Webcam",
        #"Devices/Graphics_Controller",
        #"Devices/Optical_Drive",
        #"Devices/CPU",
        #"Devices/Memory",
        #"Devices/Display",
        #"Devices/Battery",
        #"Devices/Storage",
        #"System_Information/Cosmetic_Grade",
        #"System_Information/LCD_Grade",
        #"System_Information/Final_Grade",
        #"System_Information/System_Notes",
        #"System_Overview",
        #"Erasure",
        "Networking",
    ]

    def __init__(self,tree:ET.Element):
        self.tree = tree

    def show_single_widget(self,parent):
        """
        used only for testing
        """
        list = []
        controller = ControllerFactory.build_controller(self.tree.find(".//System_Information/Unique_Identifier"))
        list.append(controller)
        list.append(ExitWindow())
        return list

    def build_widget_list(self,parent,controller_list) -> list[ITADController]:
        widget_list = self.initialize_controllers_from_list(controller_list,parent)
        widget_list.append(ExitWindow()) 
        return widget_list

    def initialize_controllers_from_list(self,node_list:dict,parent:QWidget) -> list:
        widgets = []
        for key in node_list:
            

            elements = self.tree.findall(".//"+key)
            
            if len(elements) == 0:
                controller = ControllerFactory.build_controller(key,self.tree,parent)
                widgets.append(controller)
            else:
                for node in elements:

                    controller = ControllerFactory.build_controller(node.tag,node,parent)
                    widgets.append(controller)
            
            

        return widgets




    