from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtCore import Qt,QObject
import xml.etree.ElementTree as ET
from Generics import ITADWidget


class BasicListView(ITADWidget):
    def __init__(self,element:ET.Element):
        super().__init__()
        self.element = element
        self.vbox = QVBoxLayout()
        self.initUI()
        self.setLayout(self.vbox)
    
    def initUI(self):
        self.build_label()
        self.build_list_widget()
    
    def build_label(self):
        self.header = QLabel()
        height = QFontMetrics(self.header.font()).height() 
        self.header.setMinimumHeight(height)
        self.vbox.addWidget(self.header)
    
    def build_list_widget(self):
        self.list_widget = CustomListWidget()
        self.list_widget.setObjectName("Object_Of_Focus")
        self.vbox.addWidget(self.list_widget)
    
class CustomListWidget(QListWidget):
    def __init__(self):
        super().__init__()

    def calc_option_width(self,font_metric:QFontMetrics,options):
        l = 0 
        for i in options:
            l = max(l,font_metric.width(i))
        return l + 7

    def addItems(self,options:list):
        font_metric = QFontMetrics(self.font())
        height = font_metric.height() * (len(options)+1)
        self.setMinimumWidth( self.calc_option_width(font_metric,options) )
        self.setMinimumHeight(height)
        super().addItems(options)