from GUIs.CustomWidgets.CustomWidgets import *

GRADE = [
    "A - No signs of wear",
    "B - Minor to moderate signs of wear",
    "C - Major signs of wear",
    "D - Excessive signs of Wear",
    "F - Failed",
]
FINAL_GRADE = [
    "A",
    "B",
    "C",
    "D",
    "F",
]

class FinalGrade(CustomListWidget):
    def __init__(self,element):
        name = element.tag.replace("_"," ")
        super().__init__(
            element,
            FINAL_GRADE,
            f"Select {name}",
            1)
    
    def pre_display_update(self,parent):
        print("test")
        cosmetic = parent.tree.find(".//System_Information/Cosmetic_Grade").text[0]
        category = parent.tree.find(".//System_Information/System_Category").text
        
        index = FINAL_GRADE.index(cosmetic)

        if "Laptop" in category or "All-In-One" in category:
            lcd = parent.tree.find(".//System_Information/LCD_Grade").text[0]
            index = max(FINAL_GRADE.index(lcd),index)

        for child in self.children():
            if isinstance(child, QListWidget):
                child.setCurrentItem(child.item(index))
                break

class GradeList(CustomListWidget):
    def __init__(self,element):
        name = element.tag.replace("_"," ")
        super().__init__(
            element,
            GRADE,
            f"Select {name}",
            1)
