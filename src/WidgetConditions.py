import re
from HardwareTests.Controllers.KeyboardTestController import KeyboardTestController


class WidgetCondidtion():
    def __init__(self,controller,tree):
        self.controller = controller
        self.tree = tree


    def verify(self):
        return True

    def check_element_for_text(self,xpath,regex):
        value = self.tree.find(xpath).text
        if value == None: return True
        matches = re.search(regex,value)
        if matches is not None:
            return True
        return False

class LaptopCondition(WidgetCondidtion):
    def verify(self):
        return self.check_element_for_text(".//System_Information/System_Category",r"Laptop")
    
class AllInOneCondition(WidgetCondidtion):
    def verify(self):
        return self.check_element_for_text(".//System_Information/System_Category",r"All-In-One")

class StorageHotplugCondition(WidgetCondidtion):
    def verify(self):
        try:
            return self.controller.element.find(".//Hotplug").text != "1"
        except:
            return True

class WidgetConditionProcessor():
    def process(controller,tree):
        if controller is None: return True
        
        key  = type(controller)
        if hasattr(controller,"element"):
            key = controller.element.tag

        if key in WIDGET_CONDITIONS:
            
            conditions = WIDGET_CONDITIONS[key]
            verfies = [ condition(controller,tree).verify() for condition in conditions ]

            if any(verfies):
                return True
            return False
        
        return True

WIDGET_CONDITIONS = {
    "LCD_Grade":[LaptopCondition,AllInOneCondition],
    "Display":[LaptopCondition,AllInOneCondition],
    "Battery":[LaptopCondition],
    "Webcam":[LaptopCondition,AllInOneCondition],
    "Storage":[StorageHotplugCondition],
    "Keyboard_Test":[LaptopCondition],
}