import xml.etree.ElementTree as ET


class DriveModel:
    def __init__(self,storage_xml:ET.Element):
        self.xml = storage_xml
        self.name = storage_xml.find(".//Name").text
        self.model = storage_xml.find(".//Model").text
        self.serial = storage_xml.find(".//Serial_Number").text
        self.size = storage_xml.find(".//Size").text
        self.path = "/dev/" + self.name

    def set_removed(self,bool:bool):
        """
        sets the Removed child tag
        """
        if bool: #set Removed (tag) 
            if not self.is_removed(): #if it doesnt already have the Removed tag
                self.xml.append(ET.Element("Removed"))
        else: #removed Removed (tag)
            if self.is_removed():
                self.xml.remove(self.xml.find("Removed"))

    def is_removed(self):
        return self.xml.find("Removed") is not None