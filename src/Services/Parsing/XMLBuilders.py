import logging
import xml.etree.ElementTree as ET
from Services.Parsing.DeviceParsers import *
from Services.Parsing.SysInfoParsers import *
from Services.Parsing.UtilParsers import *


class XMLBuilder:
    def __init__(self):
        self.logger = logging.getLogger("XMLBuilder")
        self.parsers = {
            "System_Chassis_Type":ChassisTypeParse(),
            "System_Manufacturer":ManufactureParser(),
            "System_Model":ModelParser(),
            "System_Serial_Number":SerialNumberParser(),
            "Webcam": WebcamParser(),
            "Graphics_Controller": GraphicsControllerParser(),
            "Optical_Drive": OpticalDriveParser(),
            "CPU": CPUParser(),
            "Memory": MemoryParser(),
            "Display": DisplayParser(),
            "Battery": BatteryParser(),
            #"Storage_Data_Collection": None,
            "Storage":StorageParser(),
            "Report_Info":ReportInfoPraser(),
        }

    def build_elements(self, element:ET.Element) -> list[ET.Element]:
        if element.tag not in self.parsers:
            return
        func = self.parsers[element.tag]
        return func.parse()
    
    def process_tree(self, root: ET.Element):
        """Process the entire XML tree, replacing elements as needed."""
        self._process_element(root)

    def _process_element(self, parent: ET.Element):
        """Recursively process elements, replacing those in parser list."""
        i = 0
        while i < len(parent):
            child = parent[i]
            
            # Check if this element needs replacement
            new_elements = self.build_elements(child)
            
            if new_elements is not None:
                # Remove the original element
                parent.remove(child)
                
                # Insert new elements at the same position
                for j, new_elem in enumerate(new_elements):
                    parent.insert(i + j, new_elem)
                
                # Skip ahead by the number of elements we inserted
                i += len(new_elements)
                
                self.logger.info(f"Replaced {child.tag} with {len(new_elements)} elements")
            else:
                # Process children of this element recursively
                self._process_element(child)
                i += 1

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
