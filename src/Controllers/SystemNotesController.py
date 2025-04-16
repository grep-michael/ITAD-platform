from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtCore import Qt,QObject
import xml.etree.ElementTree as ET
from Generics import ITADView
from Views.SystemNotesView import SystemNotesView

class SystemNotesController(ITADView):
    def __init__(self,element:ET.Element,parent):
        super().__init__()
        self._parent = parent
        self.element = element
        self.vbox = QVBoxLayout()
        self.initUI()
        self.setLayout(self.vbox)
    
    def initUI(self):
        self.view = SystemNotesView()
        self.connect_view()
        self.vbox.addWidget(self.view)

    def handle_text_change(self,text_area:QTextEdit):
        self.element.text = text_area.toPlainText().upper()

    def connect_view(self):
        header:QLabel = self.view.findChild(QLabel,"header")
        header.setText(self.element.tag.replace("_"," "))

        self.view.text_area.setPlainText(self.element.text)
        self.view.text_area.textChanged.connect(lambda tb=self.view.text_area: self.handle_text_change(tb))
        self.view.text_area.set_parent(self._parent)

    def verify(self):
        return True