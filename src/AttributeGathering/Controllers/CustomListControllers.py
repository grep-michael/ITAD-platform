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
    "(A) C6 - Used, No Signs of Wear",
    "(B) C5 - Used, Minor Signs of Wear",
    "(B-) C4 - Used, Moderate Signs of Wear",
    "(C) C3 - Used, Major Signs of Wear",
    "(D) C2 - Used, Excessive Signs of Wear",
    "(F) C1 - Non-Functional/BER",
]
#FINAL_GRADE = [
#    "(A) C6 - Used, No Signs of Wear",
#    "(B) C5 - Used, Minor Signs of Wear",
#    "(B-) C4 - Used, Moderate Signs of Wear",
#    "(C) C3 - Used, Major Signs of Wear",
#    "(D) C2 - Used, Excessive Signs of Wear",
#    "(F) C1 - Non-Functional/BER",
#]

class FinalGradeController(BasicListController):
    def __init__(self,element):
        name = element.tag.replace("_"," ")
        super().__init__(
            element,
            GRADE,
            f"Select {name}",
            1)

    def pre_display_update(self,parent):

        cosmetic = parent.tree.find(".//System_Information/Cosmetic_Grade").text
        category = parent.tree.find(".//System_Information/System_Category").text
        
        index = GRADE.index(cosmetic)

        if "Laptop" in category or "All-In-One" in category:
            lcd = parent.tree.find(".//System_Information/LCD_Grade").text
            index = max(GRADE.index(lcd),index)
        
        self.set_selected_item(index)

class GradeListController(BasicListController):

    def __init__(self,element):
        name = element.tag.replace("_"," ")
        super().__init__(
            element,
            GRADE,
            f"Select {name}",
            1)
