from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtCore import Qt,QObject
import xml.etree.ElementTree as ET
from Generics import ITADWidget

TAG_BLACKLIST = {
    "Storage":["Hotplug","Removed"],
}

class BasicNodeView(ITADWidget):

    def __init__(self):
        super().__init__()
        #self.element:ET.Element = el

        self.vbox = QVBoxLayout()
        self.text_boxes:list[QLineEdit] = []

        self.setLayout(self.vbox)
        self.max_height = self.calc_height()

    def calc_height(self):        
        height = 0
        for i in range(self.vbox.count()):
            child = self.vbox.itemAt(i)
            try:
                height+= QFontMetrics(child.font()).height()#+self.font_factor
            except:
                height+= child.minimumSize().height()#+self.font_factor

        return height

    def build_from_element(self,element:ET.Element):
        header = QLabel(element.tag.replace("_"," "))
        header.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
        self.vbox.addWidget(header)
        if len(list(element)) == 0:
            txt_display = self.create_text_display(element)
            self.vbox.addWidget(txt_display)
        
        for child in element:
            blacklist = TAG_BLACKLIST.get(element.tag,None)
            if blacklist:
                if child.tag in blacklist: continue 

            row = QHBoxLayout()
            label = QLabel(child.tag)
            row.addWidget(label)
            txt_display = self.create_text_display(child)
        
            row.addWidget(txt_display)
            
            self.vbox.addLayout(row)

    def create_text_display(self,element:ET.Element):
        text_display = QLineEdit(self)
        text_display.setText(element.text)
        text_display.setObjectName(element.tag)
        size = QFontMetrics(text_display.font()).horizontalAdvance(text_display.text())+7 #+ self.font_factor
        size = min(size,500)
        text_display.setMinimumWidth(size)
        self.text_boxes.append(text_display)
        return text_display
        