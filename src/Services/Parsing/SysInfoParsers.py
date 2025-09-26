import re,logging
import xml.etree.ElementTree as ET
from Utilities.Utils import ErrorlessRegex,REGEX_ERROR_MSG

class BaseSysParser:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.re = ErrorlessRegex()
        with open("specs/system.txt") as f:
            self.system = f.read()
    
    def create_element(self, tag, text:str=None):
        element = ET.Element(tag)
        if text is not None:
            text = self.check_default(text,tag)
            element.text = text
        return element

    def check_default(self,text,name):
        if "Default string" in text:
            import tkinter as tk
            from tkinter import simpledialog
            root = tk.Tk()
            root.withdraw() 
            user_input = simpledialog.askstring("Input", f"Default string detected, enter new {name}:")
            root.destroy()
            return user_input.strip()
        else:
            return text.strip()

class ChassisTypeParse(BaseSysParser):
    def parse(self):
        chassis = self.re.find_first([r"description: (.*)"],self.system)
        return [self.create_element("System_Chassis_Type",chassis)]        

class ManufactureParser(BaseSysParser):
    def parse(self):
        manufacturer = self.re.find_first([r"vendor:(.*)"],self.system)

        if "HEWLETT-PACKARD" in manufacturer.upper():
            manufacturer = "HP"
        if "dell" in manufacturer.lower():
            manufacturer = "DELL"

        return [self.create_element("System_Manufacturer",manufacturer)]

class ModelParser(BaseSysParser):
    
    model_table = {
        "lenovo":[
            r"version:(.*)",
            r"product:(.*)\(",
            ],
        
        "default":[
            r"product:(.*)\(",
            r"version:(.*)",
        ]
    }
    
    def parse(self):

        vendor = self.re.find_first([r"vendor: (.*)"],self.system).lower().strip()
        if vendor in ModelParser.model_table:
            L_regex = ModelParser.model_table[vendor]
        else:
            L_regex = ModelParser.model_table["default"]

        model = self.re.find_first(L_regex,self.system)
        if model != REGEX_ERROR_MSG:
            model = model.upper()
        return [self.create_element("System_Model",model)] 

class SerialNumberParser(BaseSysParser):
    def parse(self):
        serial = self.re.find_first([r"serial:(.*)"],self.system)
        if serial != REGEX_ERROR_MSG:
            serial = serial.upper()
        return [self.create_element("System_Serial_Number",serial)]
