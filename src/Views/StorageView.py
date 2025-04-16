from Generics import ITADView
from Views.BasicNodeView import BasicNodeView
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtCore import Qt
import xml.etree.ElementTree as ET


class StorageView(BasicNodeView):
    def __init__(self):
        super().__init__()
        
    def build_from_element(self,element):
        super().build_from_element(element)
        hbox = QHBoxLayout()
        self.remove_button = QPushButton(text="Remove Drive")
        hbox.addWidget(self.remove_button)
        self.vbox.insertLayout(1,hbox)
