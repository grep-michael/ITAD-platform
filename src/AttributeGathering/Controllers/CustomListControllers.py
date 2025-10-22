from AttributeGathering.Controllers.BasicListController import BasicListController
from PyQt5.QtWidgets import QListWidget
from Utilities.Config import Config


class SystemCategoryController(BasicListController):
    def __init__(self, element):
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
            )


class TechIDController(BasicListController):
    def __init__(self, element):
        prefix = Config.OPERATOR_PREFIX + "-"
        tech_id_total = int(Config.OPERATOR_COUNT)
        tech_ids = [prefix+str(i+1) for i in range(tech_id_total)]
        super().__init__(element, tech_ids, "Select Tech ID")

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

class FinalGradeController(BasicListController):
    def __init__(self,element):
        name = element.tag.replace("_"," ")
        super().__init__(
            element,
            FINAL_GRADE,
            f"Select {name}",
            1)

    def pre_display_update(self,parent):
        return 
        # neutured due to grading changing
        cosmetic = parent.tree.find(".//System_Information/Cosmetic_Grade").text[0]
        category = parent.tree.find(".//System_Information/System_Category").text
        
        index = FINAL_GRADE.index(cosmetic)

        if "Laptop" in category or "All-In-One" in category:
            lcd = parent.tree.find(".//System_Information/LCD_Grade").text[0]
            index = max(FINAL_GRADE.index(lcd),index)
        
        self.set_selected_item(index)

class GradeListController(BasicListController):

    def __init__(self,element):
        name = element.tag.replace("_"," ")
        super().__init__(
            element,
            GRADE,
            f"Select {name}",
            1)
