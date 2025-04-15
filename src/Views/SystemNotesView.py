from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtCore import Qt,QObject
import xml.etree.ElementTree as ET
from Generics import ITADWidget

class SystemNotesView(ITADWidget):
    def __init__(self):
        super().__init__()
        self.vbox = QVBoxLayout()
        self.build_layout()
        self.setLayout(self.vbox)
    
    def build_layout(self):

        header = QLabel()
        header.setObjectName("header")
        header.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
        self.vbox.addWidget(header)

        instruction_label = QLabel("comma seperate notes, program will auto capitilize")
        instruction_label.setAlignment(Qt.AlignHCenter)
        self.vbox.addWidget(instruction_label)

        self.text_area = SystemNotesTextEditWidget()
        self.text_area.setObjectName("Object_Of_Focus")
        self.text_area.setMinimumWidth(500)

        self.vbox.addWidget(self.text_area)

class SystemNotesTextEditWidget(QTextEdit):
    def __init__(self):
        super().__init__()
    
    def set_parent(self,parent):
        self._parent = parent

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter) and self._parent:
            self._parent.keyPressEvent(event)
            return  # Ignore Enter key press
        super().keyPressEvent(event) 