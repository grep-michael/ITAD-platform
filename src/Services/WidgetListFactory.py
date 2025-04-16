from PyQt5.QtWidgets import *
from Controllers import *
from Erasure.app import *
from Views.ExitWindowView import ExitWindow
import xml.etree.ElementTree as ET

SYSTEM_SPEC_GATHERING_LIST = {
    "System_Information/Unique_Identifier":BasicNodeController,
    "System_Information/Tech_ID":TechIDController,
    "System_Information/System_Category":SystemCategoryController,
    "Devices/Webcam":WebcamController,
    "Devices/Graphics_Controller":BasicNodeController,
    "Devices/Optical_Drive":BasicNodeController,
    "Devices/CPU":BasicNodeController,
    "Devices/Memory":BasicNodeController,
    "Devices/Display":BasicNodeController,
    "Devices/Battery":BasicNodeController,
    "Devices/Storage":StorageController,
    "System_Information/System_Notes":SystemNotesController,
    "System_Information/Cosmetic_Grade":GradeListController,
    "System_Information/LCD_Grade":GradeListController,
    "System_Information/Final_Grade":FinalGradeController,
}


class WidgetListFactory():
    """
    Return a list of Controllers for the application to loop over
    """
    def __init__(self,tree:ET.Element):
        self.tree = tree
        self.root_path = ".//SYSTEM_INVENTORY/"

    def show_single_widget(self,parent):
        """
        used only for testing
        """
        list = []
        
        list.append(BasicNodeController(self.tree.find(".//System_Information/Unique_Identifier")))
        list.append(ExitWindow())
        return list

    def build_widget_list(self,parent):
        return self.show_single_widget(parent)
        widget_list = self.initialize_controllers_from_association_dict(SYSTEM_SPEC_GATHERING_LIST,parent)

        widget_list.append(OverviewController(widget_list.copy()))
        widget_list.append(ErasureApp(self.tree,parent))
        widget_list.append(ExitWindow()) 
        return widget_list

    def initialize_controllers_from_association_dict(self,class_association_list:dict,parent:QWidget) -> list:
        widgets = []
        for element_path,controller_class in class_association_list.items():
            elements = self.tree.findall(".//"+element_path)
            for node in elements:
                controller = self.create_controller(controller_class,node,parent)
                widgets.append(controller)
        return widgets

    def create_controller(self,controller_class,xml_element,parent_window:QWidget):

        if controller_class == SystemNotesController:
            return controller_class(xml_element, parent_window)

        elif controller_class == BasicNodeController:
            return controller_class(xml_element)

        else:
            return controller_class(xml_element)


    