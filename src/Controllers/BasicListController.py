from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtCore import Qt,QObject
import xml.etree.ElementTree as ET
from Generics import ITADView
from Views.BasicListView import BasicListView


class BasicListController(ITADView):

    def __init__(self,element:ET.Element,options:list,friendly_label:str=None,default_option=0):
        super().__init__()
        self.element = element
        self.options = options
        self.default_option = default_option
        self.friendly_label = element.tag.replace("_"," ") if friendly_label is None else friendly_label
        self.vbox = QVBoxLayout()
        self.initUI()
        self.vbox.addStretch()
        self.setLayout(self.vbox)

    def verify(self):
        return True

    def set_selected_item(self,index=0):
        self.view.list_widget.setCurrentItem(
            self.view.list_widget.item(index)
            )

    def initUI(self):
        self.view = BasicListView(self.element)
        self.setup_view()

    def text_change(self,text):
        self.element.text = text

    def setup_view(self):
        self.view.header.setText(self.friendly_label)

        self.view.list_widget.addItems(self.options)
        self.view.list_widget.currentTextChanged.connect(self.text_change)
        self.set_selected_item(self.default_option)
        #self.view.list_widget.setCurrentItem(
        #    self.view.list_widget.item(self.default_option)
        #    )
        
        
        self.view.adjustSize()
        self.vbox.addWidget(self.view)
        self.adjustSize()

    def setFocus(self):
        # Override setFocus to focus the list widget
        if self.view.list_widget:
            self.view.list_widget.setFocus()
        else:
            super().setFocus()