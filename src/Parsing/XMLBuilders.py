import logging
import xml.etree.ElementTree as ET
from Parsing.DeviceParsers import *
from Parsing.SysInfoParsers import *


class XMLBuilder:
    def __init__(self):
        raise NotImplementedError()

    def build_xml_tree(self,root_tree,name):
        root = ET.Element(name)
        for child in root_tree.find(name):
            if child.tag in self.parsers:
                self.logger.info(f"Parsing {child.tag}")
                new_children = self.parsers[child.tag].parse()
                for new_child in new_children:
                    root.append(new_child)
            else:
                root.append(child)
                self.logger.info(f"No parser for tag {child.tag}")
        return root



class SysInfoXMLBuilder(XMLBuilder):
    def __init__(self):
        self.logger = logging.getLogger("SysInfoXMLBuilder")
        self.parsers = {
            "System_Chassis_Type":ChassisTypeParse(),
            "System_Manufacturer":ManufactureParser(),
            "System_Model":ModelParser(),
            "System_Serial_Number":SerialNumberParser(),
        }
    
    def build_xml_tree(self, root_tree:ET.Element):
        return super().build_xml_tree(root_tree,"System_Information")
        

class DeviceXMLBuilder(XMLBuilder):
    def __init__(self):
        self.logger = logging.getLogger("DeviceXMLBuilder")
        self.parsers = {
            "Webcam": WebcamParser(),
            "Graphics_Controller": GraphicsControllerParser(),
            "Optical_Drive": OpticalDriveParser(),
            "CPU": CPUParser(),
            "Memory": MemoryParser(),
            "Display": DisplayParser(),
            "Battery": BatteryParser(),
            #"Storage_Data_Collection": None,
            "Storage":StorageParser(),
            
        }
    
    def build_xml_tree(self, root_tree:ET.Element):
        return super().build_xml_tree(root_tree,"Devices")
        