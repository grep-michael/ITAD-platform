from GUIs.BaseWidgets import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtCore import Qt
from Utils.InputVerification import Verifier
import xml.etree.ElementTree as ET



class SystemCategory(CustomList):
    
    def __init__(self, element,parent):
        options = [
            "Desktop",
            "Laptop",
            "Server",
            "All-In-One"
        ]
        super().__init__(
            element,
            options,
            f"Select Category",
            parent)


GRADE = [
    "A",    
    "B",
    "C",
    "D",
    "F",
]

class LowestGrade(CustomList):
    def __init__(self, element,parent):
        name = element.tag.replace("_"," ")
        super().__init__(
            element,
            GRADE,
            f"Select {name}",
            parent,
            1)
    
    def pre_display_update(self,parent):
        cosmetic = parent.tree.find(".//System_Information/Cosmetic_Grade").text
        category = parent.tree.find(".//System_Information/System_Category").text
        
        index = GRADE.index(cosmetic)

        if "Laptop" in category or "All-In-One" in category:
            lcd = parent.tree.find(".//System_Information/LCD_Grade").text
            index = max(GRADE.index(lcd),index)

        for child in self.children():
            if isinstance(child, QListWidget):
                child.setCurrentItem(child.item(index))
                break

class GradeList(CustomList):
    def __init__(self, element,parent):
        name = element.tag.replace("_"," ")
        super().__init__(
            element,
            GRADE,
            f"Select {name}",
            parent,
            1)

class TechIDList(CustomList):
    def __init__(self, element,parent):
        prefix = "IN-"
        tech_id_total = 7
        tech_ids = [prefix+str(i+1) for i in range(tech_id_total)]
        super().__init__(
            element,
            tech_ids,
            "Select Tech ID",parent)

