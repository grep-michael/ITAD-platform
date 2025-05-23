from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtCore import Qt,QObject
import xml.etree.ElementTree as ET
from Generics import ITADController
from AttributeGathering.Views.SystemNotesView import SystemNotesView

class SystemNotesController(ITADController):
    def __init__(self,element:ET.Element,parent):
        super().__init__()
        self._parent = parent
        self.element = element

    def handle_text_change(self,text_area:QTextEdit):
        self.element.text = text_area.toPlainText().upper()

    def connect_view(self,view:SystemNotesView):
        self.view:SystemNotesView = view

        header:QLabel = self.view.findChild(QLabel,"header")
        header.setText(self.element.tag.replace("_"," "))
        
        self.view.text_area.setPlainText(self.element.text)
        self.view.text_area.textChanged.connect(lambda tb=self.view.text_area: self.handle_text_change(tb))
        self.view.text_area.set_parent(self._parent)

    def verify(self):
        return True

    def setFocus(self):
        self.view.setFocus()