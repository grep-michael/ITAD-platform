from GUIs.BaseWidgets import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtCore import Qt
from Utilities.InputVerification import Verifier
import xml.etree.ElementTree as ET



class ExitWindow(QWidget):
    def __init__(self):
        super().__init__()

class NotesWidget(QWidget):
    def __init__(self,el,parent):
        super().__init__()
        self._parent = parent
        self.element = el
        self.vbox = self.create_layout()
        self.setLayout(self.vbox)
    
    def text_changed(self,text_area:QTextEdit):
        text_area.associated_xml.text = text_area.toPlainText().upper()

    def verify(self):
        return True
    
    def create_layout(self):
        vbox = QVBoxLayout()

        header = QLabel(self.element.tag.replace("_"," "))
        header.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
        vbox.addWidget(header)

        instruction_label = QLabel("comma seperate notes, program will auto capitilize")
        instruction_label.setAlignment(Qt.AlignHCenter)
        vbox.addWidget(instruction_label)

        text_area = CustomTextEdit(self._parent)
        text_area.setObjectName("Object_Of_Focus")
        text_area.associated_xml = self.element
        text_area.textChanged.connect(lambda tb=text_area: self.text_changed(tb))
        text_area.setPlainText(self.element.text)
        text_area.setMinimumWidth(500)

        vbox.addWidget(text_area)
        return vbox

class CustomTextEdit(QTextEdit):
    def __init__(self,parent):
        super().__init__()
        self._parent = parent

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self._parent.keyPressEvent(event)
            return  # Ignore Enter key press
        super().keyPressEvent(event) 
        

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

class FinalGrade(CustomList):
    def __init__(self, element,parent):
        name = element.tag.replace("_"," ")
        super().__init__(
            element,
            FINAL_GRADE,
            f"Select {name}",
            parent,
            1)
    
    def pre_display_update(self,parent):
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

