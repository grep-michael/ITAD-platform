from Utilities.Utils import ErrorlessRegex,REGEX_ERROR_MSG,count_by_key_value,CommandExecutor
from Utilities.PciBlobParsing import *
import xml.etree.ElementTree as ET
import re,logging,math,subprocess,os
from collections import Counter,defaultdict
from pathlib import Path


class BaseDeviceParser:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.re = ErrorlessRegex()
    
    def read_spec_file(self, filename):
        with open(f"specs/{filename}", "r") as f:
            return f.read()
    
    def create_element(self, tag, text=None):
        element = ET.Element(tag)
        if text is not None:
            element.text = text
        return element
class MemoryParser(BaseDeviceParser):
    def parse(self):
        data = self.read_spec_file("memory.txt")
        memorySegments =  self.re.find_all(r"Memory Device\n([\s\S]*?)(?=\n\s*Handle|$)",data)
        returnList = []
        memory_xml = self.create_element("Memory")
        returnList.append(memory_xml)

        def create_child(tag,data):
            xml = self.create_element(tag,data.strip())
            memory_xml.append(xml)
        UNITS = {
            "B":  1,
            "KB": 1024,
            "MB": 1024**2,
            "GB": 1024**3,
            "TB": 1024**4,
        }
        def parse_size(size_str: str) -> int:
            """'15 GB' -> 16106127360"""
            match = re.match(r'([\d.]+)\s*([A-Za-z]+)', size_str.strip())
            if not match:
                return 0#ValueError(f"Unrecognized size format: {size_str!r}")
            value, unit = float(match.group(1)), match.group(2).upper()
            if unit not in UNITS:
                return 0
            return int(value * UNITS[unit])

        def format_size(num_bytes: int) -> str:
            """16106127360 -> '15.0 GB'"""
            for unit in reversed(list(UNITS)):
                if num_bytes >= UNITS[unit]:
                    return f"{num_bytes / UNITS[unit]:.4g} {unit}"
            return f"{num_bytes} B"

        create_child("Slots",str(len(memorySegments)))
        highestSpeed = 0
        totalCapacity = 0
        occupiedSlots = 0
        ramType = ""

        for segment in memorySegments:
            width = self.re.find(r"Total Width:\s*(.+)",segment)
            if width == "Unknown" or width == REGEX_ERROR_MSG:
                continue
            deviceXml = self.create_element("Memory_Device")
            occupiedSlots += 1

            speed = int(self.re.find(r"Speed:\s*(\d+) MT",segment))
            if speed > highestSpeed:
                highestSpeed = speed
            
            size = parse_size(self.re.find(r"Size:\s*(.*)",segment))
            totalCapacity += size

            deviceXml.append(
                self.create_element("Size",format_size(size))
            )
            deviceXml.append(
                self.create_element("Speed",f"{highestSpeed} MHz")
            )
            deviceXml.append(
                self.create_element("Serial_Number",self.re.find(r"Serial Number: (.*)",segment))
            )
            ramType = self.re.find(r"Type: (.*)",segment)
            deviceXml.append(
                self.create_element("Type",ramType)
            )
            returnList.append(deviceXml)

        create_child("Occupied_Slots",str(occupiedSlots))
        create_child("Size",format_size(totalCapacity))
        create_child("Type",ramType)
        create_child("Speed",f"{highestSpeed} MHz")

        self.logger.info("Memory found")
        return returnList

if __name__ == "__main__":
    parser = MemoryParser()
    print(parser.parse())