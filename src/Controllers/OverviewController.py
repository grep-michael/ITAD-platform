from Generics import ITADView
import xml.etree.ElementTree as ET
from PyQt5.QtWidgets import *
from Views.OverviewView import OverviewView


class OverviewController(ITADView):
    def __init__(self,controllers:list):
        super().__init__()
        self.controllers = controllers
        self.vbox = QVBoxLayout()
        self.view = OverviewView()
        self.vbox.addWidget(self.view)
        self.setLayout(self.vbox)
    
    def pre_display_update(self,parent):
        for view in self.view.child_views:
            view.deleteLater()

        for controller in self.controllers:
            self.view.add_view(controller.view)

    def connect_view(self,view:OverviewView):
        #unused for now
        self.view = view
        self.load_views()
    
    def adjustSize(self):
        return self.view.adjustSize()
    
    
    def verify(self):
        return True


        