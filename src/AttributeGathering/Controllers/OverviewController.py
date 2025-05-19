from Generics import ITADView,ITADController
import xml.etree.ElementTree as ET
from PyQt5.QtWidgets import *
from AttributeGathering.Views.OverviewView import OverviewView
from AttributeGathering.Controllers import BasicNodeController,StorageController,WebcamController




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
        self.view.child_views.clear()
        for controller in self.controllers:
            self.view.add_view(controller.view)

    def connect_view(self,view:OverviewView):
        self.view:OverviewView = view

    def steal_controllers_from_list(self,controller_list:list[ITADController]):
        for controller in controller_list:
            if hasattr(controller, "element") and controller.element.tag in OverviewController.WHITELIST:
                self.controllers.append(controller)
        
    def verify(self):
        return True


        