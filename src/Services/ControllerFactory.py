import xml.etree.ElementTree as ET


from Controllers import *
from Views import *
from Generics import *

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
}

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
}


class ControllerFactory():

    def build_controller_from_element(element:ET.Element,parent=None):
        if not element.tag in TAG_CONTROLLER:
            raise Exception("no controller for element {} found".format(element.tag))
        
        controller:ITADController = TAG_CONTROLLER[element.tag]
        view = ViewFactory.get_view_for_controller(controller)

        if controller == SystemNotesController:
            controller = controller(element, parent)
        else:
            controller = controller(element)

        controller.connect_view(view())

        return controller


class ViewFactory():
    def get_view_for_controller(controller_class:ITADController):
        if controller_class in CONTROLLER_VIEW_LIST:
            return CONTROLLER_VIEW_LIST[controller_class]
        raise Exception("No view for controller {}".format(controller_class))