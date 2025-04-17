from Generics import ITADView,ITADController
import xml.etree.ElementTree as ET
from PyQt5.QtWidgets import *
from Views.OverviewView import OverviewView
from Controllers import BasicNodeController,StorageController,WebcamController




class OverviewController(ITADController):
    """
    Overview of the current XML
    """

    WHITELIST = {
        "Unique_Identifier":BasicNodeController,
        "Webcam":WebcamController,
        "Graphics_Controller":BasicNodeController,
        "Optical_Drive":BasicNodeController,
        "CPU":BasicNodeController,
        "Memory":BasicNodeController,
        "Display":BasicNodeController,
        "Battery":BasicNodeController,
        "Storage":StorageController,
    }

    def __init__(self,tree:ET.Element):
        super().__init__()
        self.tree = tree
        self.controllers:list[ITADController] = []
    
    def pre_display_update(self,parent):
        for view in self.view.child_views:
            view.deleteLater()

        for controller in self.controllers:
            self.view.add_view(controller.view)

    def connect_view(self,view:OverviewView):
        self.view:OverviewView = view
        

    def steal_controllers_from_list(self,controller_list:list[ITADController]):
        for controller in controller_list:
            if controller.element.tag in OverviewController.WHITELIST:
                self.controllers.append(controller)

            
    
    def verify(self):
        return True


        