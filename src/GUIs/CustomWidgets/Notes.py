from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from GUIs.CustomWidgets import ITADWidget

class NotesWidget(ITADWidget):
    def __init__(self,parent,el):
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
 