import xml.etree.ElementTree as ET


from Controllers import *
from Views import *
from Generics import *
from Erasure.Controllers.ErasureWindowController import *
from Erasure.Views.ErasureWindowView import *


TAG_CONTROLLER = {
    "Unique_Identifier":BasicNodeController,
    "Tech_ID":TechIDController,
    "System_Category":SystemCategoryController,
    "Webcam":WebcamController,
    "Graphics_Controller":BasicNodeController,
    "Optical_Drive":BasicNodeController,
    "CPU":BasicNodeController,
    "Memory":BasicNodeController,
    "Display":BasicNodeController,
    "Battery":BasicNodeController,
    "Storage":StorageController,
    "System_Notes":SystemNotesController,
    "Cosmetic_Grade":GradeListController,
    "LCD_Grade":GradeListController,
    "Final_Grade":FinalGradeController,
    "System_Overview":OverviewController,
    "Erasure":ErasureWindowController,
}


class ControllerFactory():
    

    # Fuck it we ball
    INITALIZED_CONTROLLERS = []

    def build_controller(element:ET.Element,key:str=None,parent=None):
        if key == None: key = element.tag

        if not key in TAG_CONTROLLER:
            raise Exception("no controller for key {} found".format(key))
        
        controller:ITADController = TAG_CONTROLLER[key]
        view = ViewFactory.get_view_for_controller(controller)
        if controller == SystemNotesController:
            controller = controller(element, parent)
        
        elif controller == OverviewController:
            controller:OverviewController = controller(element)
            controller.steal_controllers_from_list(ControllerFactory.INITALIZED_CONTROLLERS)
        
        elif controller == ErasureWindowController:
            controller:ErasureWindowController = controller(parent)
            controller.create_drive_models(element)
            
        else:
            controller = controller(element)

        controller.connect_view(view())
        ControllerFactory.INITALIZED_CONTROLLERS.append(controller)
        return controller


CONTROLLER_VIEW_LIST = {
    BasicNodeController:BasicNodeView,
    BasicListController: BasicListView,
    TechIDController:BasicListView,
    SystemCategoryController:BasicListView,
    WebcamController:WebCamView,
    StorageController:StorageView,
    SystemNotesController:SystemNotesView,
    GradeListController:BasicListView,
    FinalGradeController:BasicListView,
    OverviewController:OverviewView,
    ErasureWindowController:ErasureWindowView
}

class ViewFactory():
    def get_view_for_controller(controller_class:ITADController):
        if controller_class in CONTROLLER_VIEW_LIST:
            return CONTROLLER_VIEW_LIST[controller_class]
        raise Exception("No view for controller {}".format(controller_class))