import re,logging
import xml.etree.ElementTree as ET
from Utilities.Utils import ErrorlessRegex
class SystemInfoParser():
    """
    Parse all nessacary files and returns the appropriate xml format:
    """
    def __init__(self,template):
        self.logger = logging.getLogger("SystemInfoParser")
        self.TEMPLATE = template
        self.re = ErrorlessRegex()

        with open("specs/system.txt") as f:
            self.system = f.read()

        self.func_table = {
            "System_Chassis_Type":self.parse_system_chassistype,
            "System_Manufacturer":self.parse_System_Manufacturer,
            "System_Model":self.parse_System_Model,
            "System_Serial_Number":self.parse_System_Serial_Number,
        }
        
    def build_xml_tree(self):
        #tree = ET.ElementTree(ET.fromstring(XML_TEMPLATE))
        tree = self.TEMPLATE
        for child in tree:
            if child.tag in self.func_table:
                child.text = self.func_table[child.tag]().strip()
        return tree   
        
    def parse_system_chassistype(self):
        return self.re.find_first([r"description: (\w*)"],self.system)
    
    def parse_System_Manufacturer(self):
        return self.re.find_first([r"vendor:(.*)"],self.system)
    
    def parse_System_Model(self):
        model = self.re.find_first([
        r"version:(.*)",
        r"product:(.*)\("
        ],self.system)
        return self.check_default(model,"Model") 

    def parse_System_Serial_Number(self):
        serial = self.re.find_first([r"serial:(.*)"],self.system)
        return self.check_default(serial,"Serial")
    
    def check_default(self,text,name):
        if "Default string" in text:
            import tkinter as tk
            from tkinter import simpledialog
            root = tk.Tk()
            root.withdraw() 
            user_input = simpledialog.askstring("Input", f"Default string detected, enter new {name}:")
            root.destroy()
            return user_input
        else:
            return text
    
